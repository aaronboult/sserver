"""Provides basic implementation templating with simple logic."""


from typing import Any, Dict, Optional
from sserver.templating.template import Template
from sserver.templating.template_renderer import (
    TemplateRenderer,
    BlockTagContents,
)
from sserver.templating.register import (
    register_inline_tag,
    register_block_tag,
)


# Alias for context
Context = Dict[str, Any]


def get(template_name: str, app_name: Optional[str]) -> Optional[Template]:
    """Get a template from `app_name` with name
    `template_name`.

    Args:
        app_name (`str`): The name of the app to get from.
        template_name (`str`): The name of the template to get.

    Returns:
        `Template` | `None`: The template object, or None if not found.
    """

    if not isinstance(template_name, str):
        raise TypeError('template_name must be of type str')

    if app_name is not None and not isinstance(app_name, str):
        raise TypeError('app_name must be of type str or None')

    return Template(template_name, app_name=app_name)


def render_to_string(template_name: str, context: Dict[Any, Any],
                     app_name: Optional[str] = None) -> str:
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

    if not isinstance(template_name, str):
        raise TypeError('template_name must be of type str')

    if not isinstance(context, dict):
        raise TypeError('context must be of type dict')

    if app_name is not None and not isinstance(app_name, str):
        raise TypeError('app_name must be of type str or None')

    template_obj = get(template_name, app_name=app_name)
    renderer = TemplateRenderer(template_obj)

    return renderer.render(context)


def load():
    """Registers builtin template tags."""

    from sserver.templating import template_tag  # noqa: F401
