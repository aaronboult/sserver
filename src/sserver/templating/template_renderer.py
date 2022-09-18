'''Template renderer.'''

import re
from typing import Any, Dict, Tuple
from sserver.templating.template import Template
from sserver.templating import template_tag, exception
from sserver.util import log


_LOGIC_TAG_SYNTAX = '{%(.+)%}'

_RENDER_BLOCK_TAGS = {
    'if': {
        'sub_tags': [
            'elif',
            'else',
        ],
        'end_tag': 'endif',
        'tag_function': 'if_block',
    },
    'for': {
        'end_tag': 'endfor',
        'tag_function': 'for_block',
    }
}

_RENDER_INLINE_TAGS = [
    'include',
]


def _deconstruct_tag(tag_match: re.Match) -> Tuple[str, str]:
    '''Deconstructs a tag match into its name and arguments.

    Args:
        tag_match (`re.Match`): The tag match to deconstruct.

    Returns:
        `Tuple[str, str]`: The tag name and arguments.
    '''

    # Cleanup the syntax contents and separate items
    syntax_contents = tag_match.group(1).strip().split(' ')

    # Get the function name and args
    func_name = syntax_contents[0]
    args = syntax_contents[1:]

    return func_name, args


class _TagLogicBlock:
    '''A logical block in a template.'''

    def __init__(self, block_start_match: re.Match):
        '''Initializes a new RenderBlock.

        Args:
            block_start_match (`re.Match`): The match object for the
                block start tag.
        '''

        self._block_start_match = block_start_match
        self._block_close_match = None
        self._sub_tag_matche_list = []

        self._tag, self._args = _deconstruct_tag(block_start_match)

    @property
    def tag(self) -> str:
        '''The tag name.

        Returns:
            `str`: The tag name.
        '''

        return self._tag

    def try_add_sub_tag(self, tag_match: re.Match) -> bool:
        '''Tries to add a sub tag to this block.

        Args:
            tag_match (`re.Match`): The matched tag.

        Returns:
            `bool`: True if the tag was added, False otherwise.
        '''

        tag_name, _ = _deconstruct_tag(tag_match)

        sub_tags = _RENDER_BLOCK_TAGS[self._tag].get('sub_tags', [])

        if tag_name in sub_tags:
            self._sub_tag_matche_list.append(tag_name)
            return True

        return False

    def check_closing_tag(self, tag_match: re.Match) -> bool:
        '''Checks if the given tag match is the closing tag for this
            block.
        
        Args:
            tag_match (`re.Match`): The matched tag.

        Returns:
            `bool`: True if the tag_match is the closing tag for this
                block, False otherwise.
        '''

        tag_name, _ = _deconstruct_tag(tag_match)

        render_block_data = _RENDER_BLOCK_TAGS[self._tag]

        if tag_name == render_block_data['end_tag']:
            self._block_close_match = tag_match
            return True

        return False

    def render(self, template_str: str, context: Dict[str, Any]) -> Tuple[str, int]:
        '''Renders the block.

        Returns:
            `Tuple[str, int]`: The rendered block and the end index of
                the block.
        '''

        _, start_tag_end = self._block_start_match.span()
        end_tag_start, end_tag_end = self._block_close_match.span()

        block_contents = template_str[
            start_tag_end:end_tag_start
        ].strip()

        parsed_args = template_tag.parse_args(self._args, context)

        tag_output = getattr(
            template_tag,
            _RENDER_BLOCK_TAGS[self._tag]['tag_function']
        )(context, block_contents, parsed_args)

        nested_template = Template()
        nested_template.set_template_str(tag_output)

        nested_raw_contents = TemplateRenderer(
            nested_template
        )._render_raw(context)

        return nested_raw_contents, end_tag_end


class TemplateRenderer:
    '''Template renderer.'''

    def __init__(self, template: Template):
        '''Initializes the template renderer.

        Args:
            template (`str`): The template to render.
        '''

        self._template = template

    def _preprocess(self, template_str: str, context: Dict[str, Any]
                    ) -> str:
        '''Preprocesses the template string.'''

        preprocessed_template_str = ''

        # Keep track of where to append from
        next_start_index = 0

        # Keep track of opened blocks to await ends, acts as queue
        opened_block = None

        # Find instances of functional syntax
        for match in re.finditer(_LOGIC_TAG_SYNTAX, template_str):
            log.log('match', match)
            match_start, match_end = match.span()

            # Deconstruct the tag
            tag_name, tag_args = _deconstruct_tag(match)

            # If no blocks are open, append the template string up to the
            # start of the match
            if opened_block == None:
                # Append the template string up to the start of the match
                preprocessed_template_str += template_str[
                    next_start_index:match_start
                ]

                next_start_index = match_end

            else:
                # Try to add sub tag first
                if not opened_block.try_add_sub_tag(match):
                    # If no sub tag added, check for closing tag
                    if opened_block.check_closing_tag(match):
                        block_str, block_end = opened_block.render(
                            template_str,
                            context,
                        )

                        next_start_index = block_end
                        preprocessed_template_str += block_str

                        opened_block = None

                continue

            if tag_name in _RENDER_BLOCK_TAGS:
                opened_block = _TagLogicBlock(match)

            elif tag_name in _RENDER_INLINE_TAGS:
                # Get the template function from template_tag module and
                # call it passing args
                preprocessed_template_str += getattr(
                    template_tag,
                    tag_name
                )(*tag_args)

            else:
                # If all aboce fails, tag is unknown
                raise exception.UnknownTagException(
                    f'Unknown tag {tag_name}'
                )

        if opened_block != None:
            raise exception.UnclosedBlockTagException(
                f'Unclosed block "{opened_block.tag}"'
            )

        # Append the rest of the template string
        preprocessed_template_str += template_str[next_start_index:]

        return preprocessed_template_str

    def _render_raw(self, context: Dict[str, Any]) -> str:
        '''Renders the template without formatting.

        Returns:
            `str`: The rendered template before substitution.
        '''

        template_str = self._template.template_str

        # Preprocess the template string
        template_str = self._preprocess(template_str, context)

        if template_str is None:
            return ''

        return template_str

    def render(self, context: Dict[str, Any]) -> str:
        '''Renders the template with the given context.

        Args:
            **context (`Any`, optional): The context to render the template
                with.

        Returns:
            `str`: The rendered template.
        '''

        return self._render_raw(context).format(**context)
