from modulefinder import Module
from sserver.log.Logger import Logger
from sserver.tool.CacheTools import CacheTools
from sserver.tool.ModuleTools import ModuleTools

#
# Config Tools
#
class ConfigTools:


    #
    # Load Config
    #
    @staticmethod
    def clear():
        Logger.log('Clearing config')
        CacheTools.delete('config')
    

    #
    # Load
    #
    @staticmethod
    def load(**kwargs):

        ConfigTools.clear()

        Logger.log('Loading config...')

        config = {}
        config_package_manifest = []


        config_filename = kwargs.get('filename')
        if config_filename == None:
            config_filename = 'config.py'
            Logger.log('No filename found in kwargs, defaulting to config.py')

        if not isinstance(config_filename, str):
            raise TypeError('config_filename must be of type str')

        include_sserver_config = kwargs.get('include_sserver_config')
        if include_sserver_config is None:
            include_sserver_config = True
            Logger.log('No include_sserver_config found in kwargs, defaulting to True')

        if not isinstance(include_sserver_config, bool):
            raise TypeError('include_sserver_config must be of type bool')


        sserver_config = {}
        if include_sserver_config:
            sserver_config = ModuleTools.get_all_from_module(
                ModuleTools.load_from_path('sserver.config'),
            )


        config_module_list = ModuleTools.load_from_filename(config_filename)

        for config_module in config_module_list:
            current_config = ModuleTools.get_all_from_module(config_module, **{
                'force_include_keys' : ['__package__']
            })

            package = current_config.pop('__package__')
            config[package] = {**sserver_config, **current_config}

            config_package_manifest.append(package)

        Logger.log('Configs', config)

        CacheTools.serialize_set_bulk({
            'config' : config,
            'config_package_manifest' : config_package_manifest
        })