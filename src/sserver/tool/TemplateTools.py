from typing import Any, Dict, Union
from jinja2 import Environment, PackageLoader, Template, select_autoescape
from sserver.log.Logger import Logger
from sserver.tool.ConfigTools import ConfigTools


#
# Template Tools
#
class TemplateTools:
    """Handles templating using Jina2."""


    @staticmethod
    def fetch(app_name: str, template_name: str) -> Union(Template, None):
        """Fetch a template from `app_name` with name
        `template_name`.

        Args:
            app_name (`str`): The name of the app to fetch from.
            template_name (`str`): The name of the template to fetch.

        Returns:
            `Template` | `None`: The template object, or None if not found.
        """

        APP_FOLDER = ConfigTools.fetch('APP_FOLDER')
        TEMPLATE_FOLDER = ConfigTools.fetch('TEMPLATE_FOLDER', app_name = app_name)
        TEMPLATE_FOLDER_PATH = f'{APP_FOLDER}.{app_name}'

        try:
            environment = Environment(
                loader = PackageLoader(TEMPLATE_FOLDER_PATH, TEMPLATE_FOLDER),
                autoescape = select_autoescape()
            )

            return environment.get_template(template_name)

        except Exception as exception:
            Logger.exception(exception)

        return None


    @staticmethod
    def render(template: Template, context: Dict[Any]) -> str:
        """Render the given `template` using `context`.

        Args:
            template (`Template`): The template to render.
            context (`Dict[Any]`): The context passed to the template.

        Returns:
            `str`: The rendered template as a string.
        """

        return template.render(**context)
    

    @classmethod
    def load(cls, app_name: str, template_name: str, context: Dict[Any]) -> str:
        """Fetch and render the given `template` in `app_name`.

        Args:
            app_name (`str`): The name of the app to fetch from.
            template_name (`str`): The name of the template to fetch.
            context (`Dict[Any]`): The context to pass to the template.

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
        
        template = cls.fetch(app_name, template_name)

        return cls.render(template, context)