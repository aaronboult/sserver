from sserver.log.Logger import Logger


#
# Module Tools
#
class ModuleTools:

    #
    # Load from filename
    # @param str filename The filename to import
    # @returns list The loaded module
    #
    @staticmethod
    def load_from_filename(filename, **kwargs):

        fromlist = kwargs.get('fromlist', [])

        modules = []

        from os import walk
        from os.path import join

        for root, dirs, files in walk('.'):
            if filename in files:
                # Join path and remove './', '.py' and replace '/' with '.'
                import_string = join(root, filename).replace('./', '').replace('.py', '').replace('/', '.')

                modules.append(__import__(import_string, fromlist=fromlist))

        return modules
    

    #
    # Get From Module
    # @param module module The module to get from
    # @param str name The name of the attribute to get
    # @param mixed default The default value
    # @returns mixed The attribute value or default
    #
    @staticmethod
    def get_from_module(module, name, default = None):
            
            if hasattr(module, name):
                return getattr(module, name)
    
            return default