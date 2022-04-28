import sys
from sserver.log.Logger import Logger
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.PathTools import PathTools
import importlib
from re import match


#
# Module Tools
#
class ModuleTools:


    #
    # Load From Filename
    # @param str filename The filename to import
    # @returns list The loaded module
    #
    @classmethod
    def load_from_filename(cls, filename, modules = None, package = None, folder_list = None):

        if modules is None:
            modules = []

        path_list = PathTools.get_path_list_to_file(filename, folder_list = folder_list)

        for path in path_list:
            import_string = path.replace('./', '').replace('.py', '').replace('/', '.')
            modules.append(cls.load_module(import_string, package = package))

        return modules


    #
    # Load Module
    # @param str path The path to load from
    # @returns module The loaded module
    #
    @classmethod
    def load_module(cls, path, package = None, suppress_errors = True):
        if package == None:
            package = sys.path[0]

        try:
            return importlib.import_module(path, package)

        except Exception as exception:
            if not suppress_errors:
                raise exception


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
    

    #
    # Get All From Module
    # @param module module The module to get from
    # @returns dict The dictionary of values in the module
    #
    @staticmethod
    def get_all_from_module(module, include_builtins = False, **kwargs):

        force_include_keys = kwargs.get('force_include_keys', [])

        if not isinstance(force_include_keys, list):
            raise TypeError('force_include_keys must be of type list')

        # Use this method over startswith(__) to allow custom module values with __
        builtin_keys = [
            '__builtins__',
            '__cached__',
            '__doc__',
            '__file__',
            '__loader__',
            '__name__',
            '__package__',
            '__spec__',
        ]

        attributes = {}

        for key, value in module.__dict__.items():
            if include_builtins is True or key in force_include_keys:
                attributes[key] = value

            else:
                if key not in builtin_keys:
                    attributes[key] = value

        return attributes


    #
    # Get App Name
    # @param str The modules name
    # @returns str The app name
    #
    @classmethod
    def get_app_name(cls, module_name):

        # Get apps folder
        APP_FOLDER = ConfigTools.fetch('app_folder')

        if APP_FOLDER is None:
            raise Exception('app_folder not set in config')

        if not isinstance(APP_FOLDER, str):
            raise TypeError('app_folder must be of type str')

        # Seperate module path
        module_path = module_name.split('.')

        # Get index of app folder
        APP_FOLDER_INDEX = module_path.index(APP_FOLDER)

        # Return app name
        return module_path[APP_FOLDER_INDEX + 1]