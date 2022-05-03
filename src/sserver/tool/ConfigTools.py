
from configparser import ConfigParser
import os
import sys
from typing import Any, Dict, Union
from sserver.config import (
    CONFIG_CACHE_KEY,
    SSERVER_CONFIG,
    PROJECT_DEFAULT_CONFIG,
    APP_DEFAULT_CONFIG,
)
from sserver.log.Logger import Logger
from sserver.tool.CacheTools import CacheTools
from sserver.tool.PathTools import PathTools


class ConfigTools:
    """Handles loading configuration files and config operations."""


    @staticmethod
    def clear():
        """Clear the config."""

        Logger.info('Clearing config')
        CacheTools.delete('config')


    @classmethod
    def load(cls, filename: str = 'config.ini', include_default_config: bool = True):
        """Load project and app config files.

        Args:
            filename (`str`, optional): The config file filename. Defaults to
                'config.py'.
            include_default_config (`bool`, optional): Whether or not to
                include default configuration values. Defaults to True.

        Raises:
            TypeError: If the `filename` is not a string.
            TypeError: If  `include_default_config` is not a boolean.
        """

        # Check filename and include_default_config
        if not isinstance(filename, str):
            raise TypeError('config_filename must be of type str')

        if not isinstance(include_default_config, bool):
            raise TypeError('include_sserver_default_config must be of type bool')


        # Clear cache if cache tools initialized
        if CacheTools.is_ready():
            cls.clear()


        Logger.info('Loading config...')


        config = {
            '__sserver__' : SSERVER_CONFIG,
        }
        config_package_manifest = []


        # Get project config
        config_parser = ConfigParser()

        # Load project config file
        PROJECT_CONFIG_PATH = os.path.join(sys.path[0], filename)
        config_parser.read(PROJECT_CONFIG_PATH)

        evalutated_config = cls.get_evaluated_config_as_dict(config_parser)

        # Load project config
        PROJECT_CONFIG = {}

        if include_default_config:
            PROJECT_CONFIG = PROJECT_DEFAULT_CONFIG

        if 'project' in evalutated_config:

            PROJECT_CONFIG = {
                **PROJECT_CONFIG,
                **evalutated_config['project']
            }

        # Add project config to config
        config['__project__'] = PROJECT_CONFIG


        # Get paths to app configs
        APP_FOLDER = PROJECT_CONFIG.get('app_folder')

        # Get list of config files in app folder
        APP_DIRECTORY_PATH = os.path.join(sys.path[0], APP_FOLDER)
        APP_DIRECTORY_LIST = PathTools.get_directory_list(
            APP_DIRECTORY_PATH
        )

        # Load configs from each app
        for APP in APP_DIRECTORY_LIST:
            if APP != '__pycache__':
                APP_CONFIG_PATH = os.path.join(APP_DIRECTORY_PATH, APP, filename)

                # Get app config
                config_parser.read(APP_CONFIG_PATH)

                evalutated_config = cls.get_evaluated_config_as_dict(config_parser)

                # Load app config
                config[APP] = {}

                if include_default_config:
                    config[APP] = APP_DEFAULT_CONFIG

                config[APP] = {
                    **config[APP],
                    **evalutated_config
                }

                # Add app to package manifest
                config_package_manifest.append(APP)


        Logger.info('Loaded Configs', config)
        Logger.info('Loaded Package Manifest', config_package_manifest)


        # Initialize cache before accessing
        CacheTools.initialize(
            host = PROJECT_CONFIG.get('cache_host'),
            port = PROJECT_CONFIG.get('cache_port'),
            decode_strings = PROJECT_CONFIG.get('cache_decode_strings'),
        )

        CacheTools.set(key_value = {
            CONFIG_CACHE_KEY : config,
            f'{CONFIG_CACHE_KEY}_package_manifest' : config_package_manifest
        })


    @classmethod
    def get_evaluated_config_as_dict(cls, config_parser: ConfigParser) -> Dict[Any, Union[str, int, float, bool]]:
        """Evaluate the dict in `config_parser`.

        Args:
            config_parser (`ConfigParser`): The config parser to get the dict
                from.

        Returns:
            `Dict[Any, str | int | float | bool]`: The evaluated dict
        """

        evaluated_dict = {}

        for section in config_parser.sections():
            evaluated_dict[section] = {}
            for key in config_parser[section]:
                evaluated_dict[section][key] = cls.evaluate_config_value(
                    config_parser,
                    section,
                    key,
                )

        return evaluated_dict


    @staticmethod
    def evaluate_config_value(config_parser: ConfigParser, section: str, key: str) -> Union[str, int, float, bool]:
        """Evaluate config value in `section` with key `key`.

        Args:
            config_parser (`ConfigParser`): The config parser to evaluate the
                value from.
            section (`str`): The section to get the value from.
            key (`str`): The key to get the value from.

        Note:
            The value will first be evaluated as an integer, followed by a
            float, boolean and finally the string value will be returned if
            all else fails.

        Returns:
            `str` | `int` | `float` | `bool`: The evaluated value.
        """

        # Nested function for testing multiple methods
        def try_evaluate(converter):
            try:
                return converter(section, key)

            except ValueError:
                return None

        value = try_evaluate(config_parser.getint)

        if value is None:
            value = try_evaluate(config_parser.getfloat)

        if value is None:
            value = try_evaluate(config_parser.getboolean)

        if value is None:
            value = config_parser[section][key]

        return value


    @classmethod
    def fetch(cls, key: str, app_name: str = '__project__') -> Union[str, int, float, bool]:
        """Fetch the value at `key` from app `app_name`.

        Args:
            key (`str`): The key to fetch the value from.
            app_name (`str`, optional): The app name to fetch from. Defaults
                to '__project__'.

        Raises:
            TypeError: If the `key` is not a string.

        Returns:
            `str` | `int` | `float` | `bool`: The value from the config.
        """

        if not isinstance(key, str):
            raise TypeError('key must be of type str')

        app_config = cls.fetch_app(app_name)

        if app_config is None:
            return None

        return app_config.get(key)


    @classmethod
    def nested_fetch(cls, *key_list: str, default: Any = None, app_name: str = '__project__') -> Union[str, int, float, bool, None]:
        """Fetch a value, descending down the config tree by iterating over `key_list`.

        Args:
            default (`Any`, optional): The value to return if no config value
                is found. Defaults to None.
            app_name (`str`, optional): The app name to fetch the config
                value from. Defaults to '__project__'.

        Returns:
            `str` | `int` | `float` | `bool` | `None`: The value from the
                config.
        """

        value = None

        if len(key_list) > 0:
            # Fetch the first key in the tree
            node = cls.fetch(key_list[0], app_name)

            # Go down the tree fetching keys
            tree_complete = True
            key_list = key_list[1:]
            for key in key_list:
                if not hasattr(node, '__getitem__'):
                    tree_complete = False
                    break

                node = node[key]

            if tree_complete:
                value = node

        return default if value is None else value


    @classmethod
    def fetch_app(cls, app_name: str) -> Dict[Any, Union[str, int, float, bool]]:
        """Fetch the config for app with name `app_name`.

        Args:
            app_name (`str`): The name of the app to fetch the config from.

        Raises:
            TypeError: If the `app_name` is not a string.

        Returns:
            `Dict[Any, Union[str, int, float, bool]]`: The app config.
        """

        Logger.info('Fetching app with name', app_name)

        if not isinstance(app_name, str):
            raise TypeError('app_name must be of type str')

        return CacheTools.get(CONFIG_CACHE_KEY).get(app_name)