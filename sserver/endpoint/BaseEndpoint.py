from sserver.mixin.OptionMixin import OptionMixin
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.ModuleTools import ModuleTools


#
# Base Endpoint
#
class BaseEndpoint(OptionMixin):

    #
    # Get
    #
    def get(self):
        return ''


    #
    # Post
    #
    def post(self):
        return ''


    #
    # Put
    #
    def put(self):
        return ''


    #
    # Patch
    #
    def patch(self):
        return ''


    #
    # Delete
    #
    def delete(self):
        return ''


    #
    # Get Config
    # @returns dict The config
    #
    def get_config(self):
        
        return ConfigTools.fetch_app(
            ModuleTools.get_app_path_from_path(self.__module__)
        )