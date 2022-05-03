from typing import Any, Dict, Union
from sserver.mixin.OptionMixin import OptionMixin
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.ModuleTools import ModuleTools
from sserver.tool.TemplateTools import TemplateTools


class BaseEndpoint(OptionMixin):
    """The base class for all endpoints to inherit from.

    Attributes:
        template (`str`, optional): The template name to use for the response.
    """


    template: str = None


    def get(self, **context: Any) -> str:
        """Handles HTTP GET requests.
        To be overriden by subclasses to provide custom functionality.

        Args:
            **context (`Any`, optional): Keyword arguments passed to the `template` as `context` if the `template` is set.

        Returns:
            `str`: The rendered `template` or an empty string.

        Raises:
            TypeError: If the `template` is set but is not a string.

        """

        template = getattr(self, 'template', None)

        # Empty response if no template set
        if template == None:
            return context

        if not isinstance(template, str):
            raise TypeError('template must be of type str')

        return TemplateTools.load(
            self.get_app_name(),
            template,
            context,
        )


    def post(self) -> str:
        """Handles HTTP POST requests.

        Note:
            To be overriden by subclasses to provide custom functionality.

        Returns:
            `str`: An empty string by default.
        """

        raise NotImplementedError('BaseEndpoint.post() not implemented')

        return ''


    def put(self) -> str:
        """Handles HTTP PUT requests.
        
        Note:
            To be overriden by subclasses to provide custom functionality.

        Returns:
            `str`: An empty string by default.
        """

        raise NotImplementedError('BaseEndpoint.put() not implemented')

        return ''


    def patch(self) -> str:
        """Handles HTTP PATCH requests.
        
        Note:
            To be overriden by subclasses to provide custom functionality.

        Returns:
            `str`: An empty string by default.
        """

        raise NotImplementedError('BaseEndpoint.patch() not implemented')

        return ''


    def delete(self) -> str:
        """Handles HTTP DELETE requests.
        
        Note:
            To be overriden by subclasses to provide custom functionality.

        Returns:
            `str`: An empty string by default.
        """

        raise NotImplementedError('BaseEndpoint.delete() not implemented')

        return ''


    def get_app_name(self) -> str:
        """Gets the app name of the calling endpoint.

        Returns:
            `str`: The app name.
        """

        return ModuleTools.get_app_name(self.__module__)


    def get_config(self) -> Dict[str, Union[str, int, float, bool, None]]:
        """Gets the config of the calling endpoint.

        Returns:
            `Dict[str, str | int | float | bool | None]`: The config in the format `{ Key : Config Value }`.

        Example:
            >>> print([endpoit_instance.get_config()])
            { 'strkey' : 'string', 'intkey' : 10, 'floatkey' : 10.5, 'boolkey' : True, 'emptykey' : None }
        """

        return ConfigTools.fetch_app(self.get_app_name())


    def get_from_config(self, *key_list: str, default: Any = None) -> Union[str, int, float, bool, None]:
        """Gets a value from the config using `*key_list` as a path through the config.

        Args:
            *key_list (`str`): The keys to use to get the value from the config.
                These keys are treated as a path through the config, similar to a tree.
            default (`Any`, optional): The value to return if the key is not found.
                Defaults to `None`.

        Returns:
            `str | int | float | bool | None`: The value from the config, or `default` if not found.

        Example:
            >>> # Using the below config
            {
                'strkey' : 'string',
                'floatkey' : 10.5,
                'nestedkey' : {
                    'intkey' : 10,
                }
            }

            >>> print(endpoit_instance.get_from_config('strkey'))
            'string'

            >>> print(endpoit_instance.get_from_config('floatkey'))
            10.5

            >>> print(endpoit_instance.get_from_config('nestedkey', 'intkey'))
            10

            >>> print(endpoit_instance.get_from_config('somekey'))
            None

            >>> print(endpoit_instance.get_from_config('somekey', default = 'Hello'))
            'Hello'
        """

        return ConfigTools.nested_fetch(*key_list, default = default, app_name = self.get_app_name())