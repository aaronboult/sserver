import configparser
import os
import sys
from sserver.config import (
    CONFIG_CACHE_KEY,
    SSERVER_CONFIG,
    PROJECT_DEFAULT_CONFIG,
    APP_DEFAULT_CONFIG,
)
from sserver.log.Logger import Logger
from sserver.tool.CacheTools import CacheTools
from sserver.tool.PathTools import PathTools

#
# Config Tools
#
class ConfigTools:


    #
    # Load Config
    #
    @staticmethod
    def clear():
        Logger.info('Clearing config')
        CacheTools.delete('config')
    

    #
    # Load
    #
    @classmethod
    def load(cls, **kwargs):

        if CacheTools.is_ready():
            cls.clear()

        Logger.info('Loading config...')


        config = {
            '__sserver__' : SSERVER_CONFIG,
        }
        config_package_manifest = []


        # Get filename for config files
        CONFIG_FILENAME = kwargs.get('filename')
        if CONFIG_FILENAME == None:
            CONFIG_FILENAME = 'config.ini'
            Logger.info('No filename found in kwargs, defaulting to config.py')

        if not isinstance(CONFIG_FILENAME, str):
            raise TypeError('config_filename must be of type str')


        # Get whether default config values should be used
        INCLUDE_DEFAULT_CONFIG = kwargs.get('include_sserver_default_config')
        if INCLUDE_DEFAULT_CONFIG is None:
            INCLUDE_DEFAULT_CONFIG = True
            Logger.info('No include_sserver_default_config found in kwargs, defaulting to True')

        if not isinstance(INCLUDE_DEFAULT_CONFIG, bool):
            raise TypeError('include_sserver_default_config must be of type bool')


        # Get project config
        config_parser = configparser.ConfigParser()

        # Load project config file
        PROJECT_CONFIG_PATH = os.path.join(sys.path[0], CONFIG_FILENAME)
        config_parser.read(PROJECT_CONFIG_PATH)

        # Load project config
        PROJECT_CONFIG = {}

        if INCLUDE_DEFAULT_CONFIG:
            PROJECT_CONFIG = PROJECT_DEFAULT_CONFIG

        if 'project' in config_parser:
            PROJECT_CONFIG = {
                **PROJECT_CONFIG,
                **dict(config_parser['project'])
            }

        # Add project config to config
        config['__project__'] = PROJECT_CONFIG


        # Get paths to app configs
        APP_FOLDER = PROJECT_CONFIG.get('APP_FOLDER')

        # Get list of config files in app folder
        APP_DIRECTORY_PATH = os.path.join(sys.path[0], APP_FOLDER)
        APP_DIRECTORY_LIST = PathTools.get_directory_list(
            APP_DIRECTORY_PATH
        )

        # Load configs from each app
        for APP in APP_DIRECTORY_LIST:
            if APP != '__pycache__':
                APP_CONFIG_PATH = os.path.join(APP_DIRECTORY_PATH, APP, CONFIG_FILENAME)

                # Get app config
                config_parser.read(APP_CONFIG_PATH)

                config[APP] = {}

                # Load app config
                config[APP] = {}

                if INCLUDE_DEFAULT_CONFIG:
                    config[APP] = APP_DEFAULT_CONFIG

                for section in config_parser.sections():
                    config[APP][section] = dict(config_parser[section])

                # Add app to package manifest
                config_package_manifest.append(APP)


        Logger.log('Project Config', PROJECT_CONFIG)
        Logger.info('Configs', config)
        Logger.info('Package Manifest', config_package_manifest)

        # Initialize cache before accessing
        CacheTools.initialize(**{
            'host' : PROJECT_CONFIG.get('CACHE_HOST'),
            'port' : PROJECT_CONFIG.get('CACHE_PORT'),
            'decode_strings' : PROJECT_CONFIG.get('CACHE_DECODE_STRINGS'),
        })

        CacheTools.set_bulk({
            CONFIG_CACHE_KEY : config,
            f'{CONFIG_CACHE_KEY}_package_manifest' : config_package_manifest
        })
    

    #
    # Fetch
    # @param str key The key to fetch from the project config
    # @returns mixed The value of the key
    #
    @classmethod
    def fetch(cls, key, app_name = '__project__'):

        Logger.log('fetching', key)
        Logger.log('with app_name', app_name)

        if not isinstance(key, str):
            raise TypeError('key must be of type str')

        app_config = cls.fetch_app(app_name)

        if app_config is None:
            return None

        return app_config.get(key)


    #
    # Fetch App
    # @param str app_name The name of the app to fetch from
    # @returns dict The apps config
    #
    @classmethod
    def fetch_app(cls, app_name):

        Logger.info('Fetching app with name', app_name)

        if not isinstance(app_name, str):
            raise TypeError('app_name must be of type str')

        return CacheTools.get(CONFIG_CACHE_KEY).get(app_name)