from typing import Any, Dict, Union
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from sserver.util import log
from sserver.util import config


def get(app_name: str, template_name: str) -> Union[Template, None]:
    """Get a template from `app_name` with name
    `template_name`.

    Args:
        app_name (`str`): The name of the app to get from.
        template_name (`str`): The name of the template to get.

    Returns:
        `Template` | `None`: The template object, or None if not found.
    """

    APP_FOLDER = config.get('app_folder')
    TEMPLATE_FOLDER = config.get('template_folder', app_name=app_name)
    TEMPLATE_FOLDER_PATH = f'{APP_FOLDER}.{app_name}'

    try:
        environment = Environment(
            loader=PackageLoader(TEMPLATE_FOLDER_PATH, TEMPLATE_FOLDER),
            autoescape=select_autoescape()
        )

        return environment.get_template(template_name)

    except Exception as exception:
        log.exception(exception)

    return None


def render(template_obj: Template, context: Dict[Any, Any]) -> str:
    """Render the given `template` using `context`.

    Args:
        template (`Template`): The template to render.
        context (`Dict[Any, Any]`): The context passed to the template.

    Returns:
        `str`: The rendered template as a string.
    """

    return template_obj.render(**context)


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

    return render(template_obj, context)
