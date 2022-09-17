'''Provides basic implementation of logicless templating.'''

from typing import Any, Dict, Optional
from sserver.template.template import Template
from sserver.template.template_renderer import TemplateRenderer

def get(app_name: str, template_name: str) -> Optional[Template]:
    """Get a template from `app_name` with name
    `template_name`.

    Args:
        app_name (`str`): The name of the app to get from.
        template_name (`str`): The name of the template to get.

    Returns:
        `Template` | `None`: The template object, or None if not found.
    """

    return Template().read(app_name, template_name)


def load(app_name: str, template_name: str, context: Dict[Any, Any]) -> str:
    """Get and render the given `template` in `app_name`.

    Args:
        app_name (`str`): The name of the app to get from.
        template_name (`str`): The name of the template to get.
        context (`Dict[Any, Any]`): The context to pass to the template.

    Raises:
        TypeError: If the `app_name` is not a string.
        TypeError: If the `template_name` is not a string.
        TypeError: If the `context` is not a dictionary.

    Returns:
        `str`: The rendered template
    """

    if not isinstance(app_name, str):
        raise TypeError('app_name must be of type str')

    if not isinstance(template_name, str):
        raise TypeError('template_name must be of type str')

    if not isinstance(context, dict):
        raise TypeError('context must be of type dict')

    template_obj = get(app_name, template_name)
    renderer = TemplateRenderer(template_obj)

    return renderer.render(context)
