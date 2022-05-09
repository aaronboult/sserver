import sys
from types import ModuleType
from typing import Any, Dict, List
from sserver.util import config
from sserver.path import path
import importlib

from sserver.util.exception import MissingConfigValueException


def load_from_filename(filename: str, package: str = None,
                       folder_list: List[str] = None) -> List[ModuleType]:
    """Load modules where the filename is `filename` inside package
    `package` searching only in folders `folder_list`, if set.

    Args:
        filename (`str`): The filename to search for.
        package (`str`, optional): The package to search in. Defaults to
            None.
        folder_list (`List[str]`, optional): The list of folders to search
            in. Defaults to None.

    Note:
        If `package` is not defined, it will be set in `load_module(...)`
        to the default value.

        If `folder_list` is defined, only files inside of a folder in
        `folder_list` will be loaded.

    Returns:
        `List[ModuleType]`: The list of loaded modules.
    """

    modules = []

    file_path_list = path.get_path_list_to_file(filename,
                                                folder_list=folder_list)

    for file_path in file_path_list:
        import_string = file_path.replace('./', '') \
                                .replace('.py', '') \
                                .replace('/', '.')

        loaded_module = load_module(import_string, package=package,
                                    suppress_errors=False)

        modules.append(loaded_module)

    return modules


def load_module(module_path: str, package: str = None,
                suppress_errors: bool = True) -> ModuleType:
    """Load a module at `module_path` in `package`.

    Args:
        module_path (`str`): The path to the module.
        package (`str`, optional): The package to load from. Defaults to
            sys.path[0].
        suppress_errors (`bool`, optional): Whether or not to allow errors
            to be raised if a module is not found. Defaults to True.

    Raises:
        exception: The caught exception, if `supress_errors` is False.

    Returns:
        `ModuleType`: The loaded module.
    """
    if package is None:
        package = sys.path[0]

    try:
        return importlib.import_module(module_path, package)

    except Exception as exception:
        if not suppress_errors:
            raise exception


def get_from_module(module: ModuleType, key: str, default: Any = None) -> Any:
    """Get `key` from module; if not found, return `default`.

    Args:
        module (`ModuleType`): The module to get from.
        key (`str`): The key to get.
        default (`Any`, optional): The value to return if `key` not found.
            Defaults to None.

    Returns:
        `Any`: The value of `key` in the module, or `default` if not
            found.
    """

    if hasattr(module, key):
        return getattr(module, key)

    return default


def get_all_from_module(module: ModuleType, include_builtins: bool = False,
                        force_include_keys: List[str] = None
                        ) -> Dict[Any, Any]:
    """Get all attributes from `module`.

    Args:
        module (`ModuleType`): The module to get from.
        include_builtins (`bool`, optional): Whether or not to include
            builtin attributes. Defaults to False.
        force_include_keys (`List[str]`, optional): The keys to ensure,
            even if excluded by `include_builtins`. Defaults to None.

    Note:
        When `include_builtins` is False the following builtins are excluded:
        - `__builtins__`
        - `__cached__`
        - `__doc__`
        - `__file__`
        - `__loader__`
        - `__name__`
        - `__package__`
        - `__spec__`

    Raises:
        TypeError: If the `force_include_keys` is not a list.

    Returns:
        `Dict[Any, Any]`: The module attributes.
    """

    if force_include_keys is None:
        force_include_keys = []

    if not isinstance(force_include_keys, list):
        raise TypeError('force_include_keys must be of type list')

    # Use list instead of startswith to only target builtins
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


def get_app_name(module_path: str) -> str:
    """Get app name from module with path `module_path`.

    Args:
        module_path (`str`): The path to the module to get the app name
            of.

    Raises:
        ConfigException: If the APP_FOLDER config value is not set.
        TypeError: If the APP_FOLDER config value is not a string.

    Returns:
        `str`: The modules app name.
    """

    # Get apps folder
    APP_FOLDER = config.get('app_folder')

    if APP_FOLDER is None:
        raise MissingConfigValueException('app_folder not set in config')

    if not isinstance(APP_FOLDER, str):
        raise TypeError('app_folder must be of type str')

    # Seperate module path
    module_path = module_path.split('.')

    # Get index of app folder
    APP_FOLDER_INDEX = module_path.index(APP_FOLDER)

    # Return app name
    return module_path[APP_FOLDER_INDEX + 1]
