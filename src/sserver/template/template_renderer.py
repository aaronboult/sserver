'''Template renderer.'''


from typing import Any, Dict
from sserver.template.template import Template


class TemplateRenderer:
    '''Template renderer.'''

    def __init__(self, template: Template):
        '''Initializes the template renderer.

        Args:
            template (`str`): The template to render.
        '''

        self._template = template


    def render(self, **context: Dict[str, Any]) -> str:
        '''Renders the template with the given context.

        Args:
            **context (`Any`, optional): The context to render the template
                with.

        Returns:
            `str`: The rendered template.
        '''

        template_str = self._template.template_str

        if template_str is None:
            return ''

        return template_str.format(**context)