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
    def load():

        ConfigTools.clear()

        Logger.log('Loading config...')

        config_list = ModuleTools.load_from_filename('config.py', **{
            'force_load_path_list' : ['sserver.config.apps']
        })

        for config in config_list:
            Logger.log('Loading config', ModuleTools.get_all_from_module(config))