from sserver.log.Logger import Logger
from sserver.mixin.OptionMixin import OptionMixin
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.ModuleTools import ModuleTools
from sserver.tool.TemplateTools import TemplateTools


#
# Base Endpoint
#
class BaseEndpoint(OptionMixin):

    #
    # Get
    #
    def get(self, **context):
        template = getattr(self, 'template', None)

        # Empty response if no template set
        if template == None:
            return ''

        if not isinstance(template, str):
            raise TypeError('template must be of type str')

        return TemplateTools.load(**{
            'app_name'      : self.get_app_name(),
            'template_name' : template,
            'context'       : context,
        })


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
    # Get App Name
    # @returns string The app name
    #
    def get_app_name(self):
        return ModuleTools.get_app_path_from_path(self.__module__)


    #
    # Get Config
    # @returns dict The config
    #
    def get_config(self):
        return ConfigTools.fetch_app(self.get_app_name())


    #
    # Get From Config
    # @param string key The key to get from the config
    # @param mixed default The default value to return if the key is not found
    #
    def get_from_config(self, key):
        return ConfigTools.fetch_from_app(self.get_app_name(), key)