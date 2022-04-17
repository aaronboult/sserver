from sserver.log.Logger import Logger
from sserver.tool.PathTools import PathTools
import importlib


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

        modules = kwargs.get('default', [])

        ModuleTools.load_from_filename_mutable(filename, modules, **kwargs)

        return modules
    

    #
    # Load from filename mutable
    # @param str filename The filename to import
    # @param list out The mutable list to append to
    #
    @staticmethod
    def load_from_filename_mutable(filename, out, **kwargs):
        if not isinstance(out, list):
            raise TypeError('Parameter out must be of type list')

        fromlist = kwargs.get('fromlist', [])
        force_load_path_list = kwargs.get('force_load_path_list', [])

        path_list = PathTools.get_path_list_to_file(filename)

        for path in path_list:
            import_string = path.replace('./', '').replace('.py', '').replace('/', '.')
            out.append(ModuleTools.load_from_path(import_string, fromlist))

        for path in force_load_path_list:
            if isinstance(path, str):
                out.append(ModuleTools.load_from_path(path))

            elif isinstance(path, dict):
                out.append(ModuleTools.load_from_path(
                    path.get('path'),
                    path.get('fromlist'),
                ))

            else:
                raise TypeError('Paths provided in force_load_path_list must be of type str or dict')
    

    #
    # Load Module From Path
    # @param str path The path to load from
    # @returns module The loaded module
    #
    @staticmethod
    def load_from_path(path, fromlist = []):
        try:
            return importlib.import_module(path)

        except:
            raise ModuleNotFoundError(f'No module found with path: {path}')


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