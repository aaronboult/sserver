'''Template renderer.'''

import re
import operator
from typing import Any, Dict, List, Optional, Tuple
from sserver.templating.template import Template
from sserver.templating import exception
from sserver.templating.template_tag import validate_args_len


_LOGIC_TAG_SYNTAX = '{%(.+)%}'

# Maps string operators onto the operator module functions
_OPERATOR_MAP = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
}


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
        self._block_close_tag_depth = 0
        self._current_sub_tag_index = -1

        self._tag, _ = _deconstruct_tag(block_start_match)

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

        if self._block_close_tag_depth > 0:
            return False

        tag_name, _ = _deconstruct_tag(tag_match)

        sub_tags = _RENDER_BLOCK_TAGS[self._tag].get('sub_tags', {})

        if tag_name in sub_tags:
            self._sub_tag_matche_list.append(tag_match)
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
        end_tag = render_block_data['end_tag']

        if tag_name == end_tag:
            if self._block_close_tag_depth > 0:
                self._block_close_tag_depth -= 1
                return False

            self._block_close_match = tag_match
            return True

        elif tag_name in _RENDER_BLOCK_TAGS:
            other_tag_end_tag = _RENDER_BLOCK_TAGS[tag_name]['end_tag']

            if other_tag_end_tag == end_tag:
                self._block_close_tag_depth += 1

        return False

    def render(self, template_str: str, context: Dict[str, Any]
               ) -> Tuple[str, int]:
        '''Renders the block.

        Returns:
            `Tuple[str, int]`: The rendered block and the end index of
                the block.
        '''

        USING_SUB_TAG = self._current_sub_tag_index > -1

        NEXT_SUB_TAG_INDEX = self._current_sub_tag_index + 1
        SUB_TAG_LEN = len(self._sub_tag_matche_list)

        CURRENT_RENDER_MATCH = self._sub_tag_matche_list[
                self._current_sub_tag_index
            ] if USING_SUB_TAG else self._block_start_match

        # Get the contents of the block using the start and end
        # matches
        _, start_tag_end = CURRENT_RENDER_MATCH.span()
        end_tag_start, end_tag_end = self._block_close_match.span()

        if SUB_TAG_LEN > 0 and SUB_TAG_LEN > NEXT_SUB_TAG_INDEX:
            end_tag_start, _ = self._sub_tag_matche_list[
                NEXT_SUB_TAG_INDEX
            ].span()

        block_contents = _TagLogicBlockContents(
            template_str[
                start_tag_end:end_tag_start
            ].strip()
        )

        # Get and parse the block arguments
        tag_name, args = _deconstruct_tag(CURRENT_RENDER_MATCH)
        parsed_args = parse_args(context, args)

        tag_function = _get_tag_function(
            self._tag,
            is_block=True,
            sub_tag=tag_name if USING_SUB_TAG else None
        )

        if USING_SUB_TAG:
            SUB_TAG_DATA = _RENDER_BLOCK_TAGS[self._tag]['sub_tags'][
                tag_name
            ]

            # If sub tag does not override tag function, use the
            # parent
            if SUB_TAG_DATA.get('tag_function') is not None:
                tag_function = SUB_TAG_DATA.get('tag_function')

        _try_validate_args_len(
            self.tag,
            parsed_args,
            is_block=True,
            sub_tag=tag_name if USING_SUB_TAG else None
        )

        tag_output: Optional[str] = tag_function(
            context, block_contents, *parsed_args
        )

        # If no output was returned, check for sub tags
        if tag_output is None:
            if len(self._sub_tag_matche_list) > 0:
                self._current_sub_tag_index += 1

                return self.render(template_str, context)

            tag_output = ''

        # Render the returned block contents
        nested_template = Template()
        nested_template.set_template_str(tag_output)

        nested_raw_contents = TemplateRenderer(
            nested_template
        )._render_raw(context)

        return nested_raw_contents, end_tag_end


class _TagLogicBlockContents(str):
    '''Contents of a tag logic block.'''

    def render(self, context: Dict[str, Any]) -> str:
        '''Renders the contents of the block.

        Args:
            context (`Dict[str, Any]`): The context to render the
                contents with.

        Returns:
            `str`: The rendered contents.
        '''

        nested_template = Template()
        nested_template.set_template_str(self)

        nested_raw_contents = TemplateRenderer(
            nested_template
        )._render_raw(context)

        return nested_raw_contents


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
        '''Preprocesses the template string.

        Args:
            template_str (`str`): The template string to preprocess.
            context (`Dict[str, Any]`): The context to preprocess the
                template with.

        Returns:
            `str`: The preprocessed template string.

        Raises:
            `UnknownTagException`: If a tag is not recognized.
            `UnclosedBlockException`: If a block is not closed.
        '''

        preprocessed_template_str = ''

        # Keep track of where to append from
        next_start_index = 0

        # Keep track of opened blocks to await ends, acts as queue
        opened_block = None

        # Find instances of functional syntax
        for match in re.finditer(_LOGIC_TAG_SYNTAX, template_str):
            match_start, match_end = match.span()

            # Deconstruct the tag
            tag_name, tag_args = _deconstruct_tag(match)

            # If no blocks are open, append the template string up to the
            # start of the match
            if opened_block is None:
                # Append the template string up to the start of the match
                preprocessed_template_str += template_str[
                    next_start_index:match_start
                ]

                next_start_index = match_end

            else:
                # Try to add sub tag first (e.g. elif, else)
                if not opened_block.try_add_sub_tag(match):
                    # If no sub tag added, check for closing tag
                    if opened_block.check_closing_tag(match):
                        # If closing tag found, render block
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
                # Get the template function and call it passing
                # parsed args
                parsed_args = parse_args(context, tag_args)

                tag_function = _get_tag_function(tag_name)
                _try_validate_args_len(tag_name, parsed_args)

                preprocessed_template_str += tag_function(
                    context, *parsed_args
                )

            else:
                # If all aboce fails, tag is unknown
                raise exception.UnknownTagException(
                    f'Unknown tag {tag_name}'
                )

        if opened_block is not None:
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

# Template tag functions


def parse_args(context: Dict[str, Any], args: List[str]) -> List[Any]:
    '''Parses the arguments passed to a tag.

    Args:
        args (`List[str]`): The arguments passed to the tag.

    Returns:
        `List[Any]`: The parsed arguments.
    '''

    parsed_args = []

    # @future Support dot notation in template, e.g. if a.b.c == d.e.f
    # @future Parse literals in template, e.g. if a == 1

    for argument in args:
        if argument in context:
            parsed_args.append(context[argument])

        else:
            parsed_args.append(argument)

    return parsed_args


def include(context: Dict[str, Any], *args) -> str:
    '''Includes a template.

    Args:
        *args (`str`): Arguments passed to the tag.

    Note:
        Expects len(args) == 1 and args[0] to be the template to
            import.
    '''

    template_to_include = Template(args[0]).template_str

    if template_to_include is None:
        template_to_include = ''

    return template_to_include


def conditional_block(context: Dict[str, Any], block_contents:
                      _TagLogicBlockContents, *args) -> Optional[str]:
    '''Renders a conditional if statement.

    Args:
        context (`Dict[str, Any]`): The context to render the block
            with.
        block_contents (`_TagLogicBlockContents`): The contents of the
            block.
        *args (`str`): Arguments passed to the tag.

    Note:
        Expects args[0] and args[2] to be the left and right operands,
            respectively, and args[1] to be the operator.

    Raises:
        `UnknownTagConditionalExpressionException`: If the conditional
            expression is not recognized.

    Returns:
        `str`: The rendered block.
    '''

    if len(args) == 0:
        return block_contents

    left_expression = args[0]
    operator = args[1]
    right_expression = args[2]

    if operator not in _OPERATOR_MAP:
        raise exception.UnknownTagConditionalExpressionException(
            f'Unknown operator {operator}'
        )

    conditional_output = _OPERATOR_MAP[operator](
        left_expression,
        right_expression
    )

    if conditional_output:
        return block_contents

    return None


def for_block(context: Dict[str, Any], block_contents:
              _TagLogicBlockContents, *args) -> str:
    '''Renders a for loop.

    Args:
        context (`Dict[str, Any]`): The context to render the block
            with.
        block_contents (`_TagLogicBlockContents`): The contents of the
            block.
        *args (`str`): Arguments passed to the tag.

    Returns:
        `str`: The rendered block.
    '''

    output = ''

    identifier = args[0]
    iterable = args[2]

    for item in iterable:
        template = Template()
        template.set_template_str(block_contents)

        renderer = TemplateRenderer(template)

        output += renderer.render({
            **context,
            identifier: item,
        })

    return output


_RENDER_BLOCK_TAGS = {
    'if': {
        'sub_tags': {
            'elif': {
                'args_len': 3,
            },
            'else': {
                'args_len': 0,
            },
        },
        'args_len': 3,
        'end_tag': 'endif',
        'tag_function': conditional_block,
    },
    'for': {
        'args_len': 3,
        'end_tag': 'endfor',
        'tag_function': for_block,
    }
}

_RENDER_INLINE_TAGS = {
    'include': {
        'args_len': 1,
        'tag_function': include,
    },
}


def _get_tag_function(tag_name: str, is_block: bool = False,
                      sub_tag: Optional[str] = None) -> callable:
    '''Gets the tag function for the given tag name.

    Args:
        tag_name (`str`): The name of the tag.
        is_block (`bool`): Whether the tag is a block tag.
        sub_tag (`str`, optional): The sub tag of the block tag.

    Returns:
        `Callable`: The tag function.

    Raises:
        `UnknownTagException`: If the tag is not recognized.
        `MissingTagFunctionException`: If the tag does not have a
            function.
    '''
    tag_data = (
        _RENDER_BLOCK_TAGS if is_block
        else _RENDER_INLINE_TAGS
    )

    if tag_name not in tag_data:
        raise exception.UnknownTagException(f'Unknown tag {tag_name}')

    tag_function = tag_data[tag_name].get('tag_function')

    if sub_tag is not None:
        if sub_tag not in tag_data[tag_name]['sub_tags']:
            raise exception.UnknownTagException(
                f'Unknown sub tag {sub_tag} for tag {tag_name}'
            )

        sub_tag_function = tag_data[tag_name]['sub_tags'][sub_tag].get(
            'tag_function'
        )

        if sub_tag_function is not None:
            tag_function = sub_tag_function

    if tag_function is None:
        raise exception.MissingTagFunctionException(
            f'Missing tag function for tag {tag_name}'
        )

    return tag_function


def _try_validate_args_len(tag_name: str, args: List[Any],
                           is_block: bool = False,
                           sub_tag: Optional[str] = None) -> bool:
    '''Tries to validate the length of the arguments passed to a tag.

    Args:
        tag_name (`str`): The name of the tag.
        args (`List[Any]`): The arguments passed to the tag.
        is_block (`bool`): Whether the tag is a block tag.
        sub_tag (`str`, optional): The sub tag, if any.

    Returns:
        `bool`: Whether the number of arguments passed to the tag is
            valid.

    Raises:
        `UnknownTagException`: If the tag is not recognized.
    '''

    tag_data = (
        _RENDER_BLOCK_TAGS if is_block
        else _RENDER_INLINE_TAGS
    )

    if tag_name not in tag_data:
        raise exception.UnknownTagException(f'Unknown tag {tag_name}')

    if sub_tag is not None:
        tag_data = tag_data[tag_name]['sub_tags']

        if sub_tag not in tag_data:
            raise exception.UnknownTagException(
                f'Unknown sub tag {sub_tag}'
            )

        tag_name = sub_tag

    expected_args_len = tag_data[tag_name].get(
        'args_len'
    )

    if expected_args_len is not None:
        validate_args_len(
            tag_name,
            args,
            expected_args_len
        )

    return True
