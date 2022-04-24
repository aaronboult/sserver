from sserver.log.Logger import Logger
from sserver.tool.CacheTools import CacheTools
from sserver.tool.ModuleTools import ModuleTools

#
# Config Tools
#
class ConfigTools:


    #
    # Config Cache Key
    #
    config_cache_key = 'sserver.config'


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

        config = {}
        config_package_manifest = []


        # Get filename for config files
        config_filename = kwargs.get('filename')
        if config_filename == None:
            config_filename = 'config.py'
            Logger.info('No filename found in kwargs, defaulting to config.py')

        if not isinstance(config_filename, str):
            raise TypeError('config_filename must be of type str')


        # Get whether default config values should be used
        include_sserver_default_config = kwargs.get('include_sserver_default_config')
        if include_sserver_default_config is None:
            include_sserver_default_config = True
            Logger.info('No include_sserver_default_config found in kwargs, defaulting to True')

        if not isinstance(include_sserver_default_config, bool):
            raise TypeError('include_sserver_default_config must be of type bool')


        # Load the default config values
        sserver_default_config = {}
        if include_sserver_default_config:
            sserver_default_config = ModuleTools.get_all_from_module(
                ModuleTools.load_module('sserver.default_config', package = __file__),
            )


        # Create list of modules to load configs from and add sserver cache to it
        # @todo Refactor to use APP_FOLDER config value
        config_module_list = ModuleTools.load_from_filename(config_filename, folder_list = ['apps'])
        config_module_list.append(
            ModuleTools.load_module(cls.config_cache_key, package = __file__)
        )

        for config_module in config_module_list:
            current_config = ModuleTools.get_all_from_module(config_module, **{
                'force_include_keys' : ['__package__']
            })

            package = current_config.pop('__package__')
            config[package] = {**sserver_default_config, **current_config}

            config_package_manifest.append(package)


        Logger.info('Configs', config)

        # Initialize cache before accessing
        # CacheTools.initialize(**{

        # })

        CacheTools.set_bulk({
            cls.config_cache_key : config,
            f'{cls.config_cache_key}_package_manifest' : config_package_manifest
        })


        # Assign the app name regex to ModuleTools
        ModuleTools.app_name_regex = cls.fetch_from_app('sserver', 'APP_NAME_REGEX')
    

    #
    # Fetch
    # @param str key The key to fetch from the server config
    # @returns mixed The value of the key
    #
    @classmethod
    def fetch(cls, key):

        if not isinstance(key, str):
            raise TypeError('key must be of type str')

        config = CacheTools.deserialize_get(cls.config_cache_key)

        return config.get('sserver').get(key)
    

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
        
        config = CacheTools.deserialize_get(cls.config_cache_key)

        if app_name in config:
            return config.get(app_name)

        else:
            raise TypeError(f'No app config with app name: {app_name}')


    #
    # Fetch From App
    # @param str app_name The name of the app to fetch from
    # @param str key The key to fetch from the app
    # @returns mixed The value of the key
    #
    @classmethod
    def fetch_from_app(cls, app_name, key):
        
        if not isinstance(key, str):
            raise TypeError('key must be of type str')
        
        config = cls.fetch_app(app_name)

        if key in config:
            return config.get(key)

        else:
            raise TypeError(f'Config with app name {app_name} does not contain key value pairs for key {key}')