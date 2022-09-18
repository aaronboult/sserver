'''Template renderer.'''

import re
from typing import Any, Dict
from sserver.templating.template import Template
from sserver.util import log


class TemplateRenderer:
    '''Template renderer.'''

    def __init__(self, template: Template):
        '''Initializes the template renderer.

        Args:
            template (`str`): The template to render.
        '''

        self._template = template

    def _preprocess(self, template_str: str) -> str:
        '''Preprocesses the template string.'''

        functional_syntax = '{%(.+)%}'
        preprocessed_template_str = ''

        # Keep track of where to append from
        next_start_index = 0

        # Find instances of functional syntax
        for match in re.finditer(functional_syntax, template_str):
            syntax_contents = match.group(1)

            match_start, match_end = match.span()

            # Append the template string up to the start of the match
            preprocessed_template_str += template_str[
                next_start_index:match_start
            ]

            next_start_index = match_end

            # Cleanup the syntax contents and separate items
            syntax_contents = syntax_contents.strip().split(' ')

            # Get the function name and args
            func_name = syntax_contents[0]
            args = syntax_contents[1:]

            # @future Allow dynamic template functions
            if func_name == 'include':
                log.log('args', args)

                template_to_include = Template(args[0]).template_str

                if template_to_include is not None:
                    preprocessed_template_str += template_to_include

        # Append the rest of the template string
        preprocessed_template_str += template_str[next_start_index:]

        return preprocessed_template_str

    def render(self, context: Dict[str, Any]) -> str:
        '''Renders the template with the given context.

        Args:
            **context (`Any`, optional): The context to render the template
                with.

        Returns:
            `str`: The rendered template.
        '''

        template_str = self._template.template_str

        # Preprocess the template string
        template_str = self._preprocess(template_str)

        if template_str is None:
            return ''

        return template_str.format(**context)
