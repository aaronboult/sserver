"""Provides an interface to interact with the cached config."""

from configparser import ConfigParser
import os, sys
from typing import Any, Dict, List, Union
from sserver.util import log, cache
from sserver.path import path


# Default sserver config
__CONFIG_CACHE_KEY = 'sserver.config'


# Idealy this should remain empty, providing maximum configuration to the
# developer
__SSERVER_CONFIG = {
}


__PROJECT_DEFAULT_CONFIG = {
    'app_folder': 'apps',
    'cache_host': 'localhost',
    'cache_port': 6379,
    'cache_string_decode ': True,
    'prefix_route_with_app_name': True,
    'static_folder': 'static',
}


__APP_DEFAULT_CONFIG = {
    'template_folder': 'templates',
    'static_image_folder': 'static/image',
    'static_css_folder': 'static/css',
    'static_js_folder': 'static/js',
}


def clear():
    """Clear the config."""

    log.info('Clearing config')
    cache.delete('config')


def load(filename: str = 'config.ini', include_default_config: bool = True):
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
        error_message = 'include_sserver_default_config must be of type bool'

        raise TypeError(error_message)

    # Clear cache if cache tools initialized
    if cache.Cache.is_ready():
        clear()

    log.info('Loading config...')

    config = {
        '__sserver__': __SSERVER_CONFIG,
    }
    config_package_manifest = []

    # Get project config
    config_parser = ConfigParser()

    # Load project config file
    PROJECT_CONFIG_PATH = os.path.join(sys.path[0], filename)
    config_parser.read(PROJECT_CONFIG_PATH)

    evalutated_config = get_evaluated_config_as_dict(config_parser)

    # Load project config
    PROJECT_CONFIG = {}

    if include_default_config:
        PROJECT_CONFIG = __PROJECT_DEFAULT_CONFIG

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
    APP_DIRECTORY_LIST = path.get_directory_list(
        APP_DIRECTORY_PATH
    )

    # Load configs from each app
    for APP in APP_DIRECTORY_LIST:
        if APP != '__pycache__':

            config[APP] = {}

            if include_default_config:
                config[APP] = __APP_DEFAULT_CONFIG

            APP_CONFIG_PATH = os.path.join(APP_DIRECTORY_PATH, APP, filename)

            if os.path.isfile(APP_CONFIG_PATH):
                # Get app config
                config_parser.read(APP_CONFIG_PATH)

                evalutated_config = get_evaluated_config_as_dict(
                    config_parser
                )

                config[APP] = {
                    **config[APP],
                    **evalutated_config
                }

            log.log('app', APP)
            log.log('loaded', config[APP])

            # Add app to package manifest
            config_package_manifest.append(APP)

    log.info('Loaded Configs', config)
    log.info('Loaded Package Manifest', config_package_manifest)

    # Initialize cache before accessing
    cache.initialize(
        host=PROJECT_CONFIG.get('cache_host'),
        port=PROJECT_CONFIG.get('cache_port'),
        string_decode=PROJECT_CONFIG.get('cache_string_decode'),
    )

    cache.set(key_value={
        __CONFIG_CACHE_KEY: config,
        f'{__CONFIG_CACHE_KEY}_package_manifest': config_package_manifest
    })


def get_evaluated_config_as_dict(config_parser: ConfigParser
                                 ) -> Dict[Any, Union[str, int, float, bool]]:
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
            evaluated_dict[section][key] = evaluate_config_value(
                config_parser,
                section,
                key,
            )

    return evaluated_dict


def evaluate_config_value(config_parser: ConfigParser, section: str, key: str
                          ) -> Union[str, int, float, bool]:
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


def get(key: str, app_name: str = '__project__',
        default: Any = None) -> Union[str, int, float, bool]:
    """Get the value at `key` from app `app_name`.

    Args:
        key (`str`): The key to get the value from.
        app_name (`str`, optional): The app name to get from. Defaults
            to '__project__'.
        default (`Any`, optional): The default value to return if the
            key is not found. Defaults to None.

    Raises:
        TypeError: If the `key` is not a string.

    Returns:
        `str` | `int` | `float` | `bool`: The value from the config.
    """

    if not isinstance(key, str):
        raise TypeError('key must be of type str')

    app_config = get_app_config(app_name)

    if app_config is None:
        return default

    if key in app_config:
        return app_config.get(key)

    return default


def mget(*keys, app_name: str = '__project__') -> List:
    pass


def nested_get(*key_list: str, default: Any = None,
               app_name: str = '__project__'
               ) -> Union[str, int, float, bool, None]:
    """Get a value, descending down the config tree by iterating over
    `key_list`.

    Args:
        default (`Any`, optional): The value to return if no config value
            is found. Defaults to None.
        app_name (`str`, optional): The app name to get the config
            value from. Defaults to '__project__'.

    Returns:
        `str` | `int` | `float` | `bool` | `None`: The value from the
            config.
    """

    value = None

    if len(key_list) > 0:
        # Get the first key in the tree
        node = get(key_list[0], app_name)

        # Go down the tree getting keys
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


def get_app_config(app_name: str
                   ) -> Dict[Any, Union[str, int, float, bool]]:
    """Get the config for app with name `app_name`.

    Args:
        app_name (`str`): The name of the app to get the config from.

    Raises:
        TypeError: If the `app_name` is not a string.

    Returns:
        `Dict[Any, Union[str, int, float, bool]]`: The app config.
    """

    log.info('Fetching app with name', app_name)

    if not isinstance(app_name, str):
        raise TypeError('app_name must be of type str')

    return cache.get(__CONFIG_CACHE_KEY).get(app_name)
