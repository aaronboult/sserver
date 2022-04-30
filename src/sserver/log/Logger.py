import sys
from typing import Any, Dict, Iterable, List, Set, Tuple


class __Empty__:
    """Class for kwarg default value.

    Note:
        This allows None to be passed and still interpreted
        as a value.
    """


class Logger:
    """Provides logging functionality.

    Attributes:
        delimiter (`str`): The delimiter to use for the log message
            between the message and the context, default ' : '
    """


    delimiter: str = ' : '


    @classmethod
    def info(cls, text: str, context: Any = __Empty__):
        """Display unformatted `text` to the console
        alongside formatted `context`, if passed.

        Args:
            text (`str`): The text to display as information.
            context (`Any`, optional): The value to be formatted and displayed
                along with the `text`. Defaults to __Empty__.

        Raises:
            TypeError: If `text` is not a string.
        """


        if not isinstance(text, str):
            raise TypeError(f'text must be of type str, got {type(text)}')

        sys.stdout.write(text)

        if context is not __Empty__:
            sys.stdout.write(f'{cls.delimiter}{cls.format(context)}')

        sys.stdout.write('\n')


    @classmethod
    def log(cls, info: Any, context: Any = __Empty__):
        """Display formatted `info` to the console
        alongside formatted `context`, if passed.

        Args:
            info (`Any`): The information to be formatted and displayed.
            context (`Any`, optional): The value to be formatted and displayed
                along with the `info`. Defaults to __Empty__.
        """


        cls.info(cls.format(info), context)
    

    @classmethod
    def label(cls, label: str, context: Any = __Empty__):
        """Display `label` as a label underlined with '#' characters,
        followed by formatted `context`, if passed.

        Args:
            label (`str`): The label to underline.
            context (Any, optional): The value to be formatted and displayed
                along with the `label`. Defaults to __Empty__.

        Raises:
            TypeError: If the `label` is not a string.
        """


        if not isinstance(label, str):
            raise TypeError(f'text must be of type str, got {type(label)}')

        hash_bar = '#' * (len(label) + 4)

        label = f'\n{hash_bar}\n# {label} #\n{hash_bar}\n\n'

        sys.stdout.write(label)

        if context is not __Empty__:
            sys.stdout.write(cls.format(context))


    #
    # Exception
    # @param Error error The error to log
    #
    @classmethod
    def exception(cls, error: Exception, reraise: bool = False):
        """Display caught exception to the console and
        optionally reraise it.

        Args:
            error (`Exception`): The caught error to display.
            reraise (`bool`, optional): Whether or not to reraise
                the error after displaying. Defaults to False.

        Raises:
            TypeError: If the `error` is not an `Exception`.
            `error`: The passed exception, raised if `reraise` is True.
        """


        if not isinstance(error, Exception):
            raise TypeError(f'error must be of type Exception, got {type(error)}')

        cls.label('Exception')
        cls.log(str(error))
        cls.linebreak()

        if reraise:
            raise error
    

    @staticmethod
    def linebreak(count: int = 1):
        """Display a linebreak to the console.

        Args:
            count (`int`, optional): The number of lines. Defaults to 1.
        """


        sys.stdout.write('\n' * count)


    #
    # Format text
    # @param str content The content to format
    # @param **kwargs Options for processing
    # @returns str The formatted content
    #
    @classmethod
    def format(cls, content: Any, **kwargs: Any) -> str:
        """Format `content` according to `kwargs` into a string.

        Note:
            This method will only format `dict`, `list`,
            `tuple` and `set` types.

        Args:
            content (`Any`): The content to format.

        Returns:
            `str`: The formatted content
        """


        format_methods = {
            dict: cls.format_dict,
            list: cls.format_list,
            tuple: cls.format_list,
            set: cls.format_list,
            str: lambda string_value: f'"{str(string_value)}"'
        }

        text = None
        content_type = type(content)

        if content_type in format_methods:
            text = format_methods[content_type](content, **kwargs)

        else:
            text = str(content)

        return text


    @classmethod
    def format_dict(cls, dict_value: Dict[Any, Any], indent_level: int = 0, **kwargs: Any) -> str:
        """Format the given `dict_value` into a string.

        Args:
            dict_value (`Dict[Any, Any]`): The dictionary to format.
            indent_level (`int`, optional): The current indent level. Defaults to 0.

        Raises:
            TypeError: If the `dict_value` is not a `dict`.
            TypeError: If the `indent_level` is not an `int`.

        Returns:
            `str`: The formatted dictionary string.
        """


        if not isinstance(dict_value, dict):
            raise TypeError(f'dct must be of type dict, got {type(dict_value)}')

        if not isinstance(indent_level, int):
            raise TypeError(f'indent_level must be of type int, got {type(indent_level)}')

        text = '{\n'
        
        for key, value in dict_value.items():
            indent_level += 1
            current_indent = '\t' * (indent_level + 1)

            formatted_value = cls.format(value, indent_level = indent_level, **kwargs)

            text += f'{current_indent}"{key}"{cls.delimiter}{formatted_value},\n'

        if text == '{\n':
            text = '\t' * (indent_level - 1) + '{}'

        else:
            text += '\t' * (indent_level) + '}'

        return text


    @classmethod
    def format_list(cls, list_value: List[Any], **kwargs: Any) -> str:
        """Format the given `list_value` into a string.

        Args:
            list_value (`List[Any]`): The list to format.

        Raises:
            TypeError: If the `list_value` is not a `list`.

        Returns:
            `str`: The formatted list string.
        """


        if not isinstance(list_value, list):
            raise TypeError(f'lst must be of type list, got {type(list_value)}')

        return cls.format_iterable(list_value, ('[', ']'), **kwargs) 
    

    @classmethod
    def format_tuple(cls, tuple_value: Tuple[Any], **kwargs: Any) -> str:
        """Format the given `tuple_value` into a string.

        Args:
            tuple_value (`Tuple[Any]`): The tuple to format.

        Raises:
            TypeError: If the `tuple_value` is not a `tuple`.

        Returns:
            `str`: The formatted tuple string.
        """


        if not isinstance(tuple_value, tuple):
            raise TypeError(f'tpl must be of type tuple, got {type(tuple_value)}')

        return cls.format_iterable(tuple_value, ('(', ')'), **kwargs)
    

    @classmethod
    def format_set(cls, set_value: Set[Any], **kwargs: Any) -> str:
        """Format the given `set_value` into a string.

        Args:
            set_value (`Set[Any]`): The set to format.

        Raises:
            TypeError: If the `set_value` is not a `set`.

        Returns:
            `str`: The formatted set string.
        """


        if not isinstance(set_value, set):
            raise TypeError(f's must be of type set, got {type(set_value)}')

        return cls.format_iterable(tuple(set_value), ('{', '}'), **kwargs)
    

    @classmethod
    def format_iterable(cls, iterable_value: Iterable, wrappers: Tuple[str], use_multiline: bool = True, indent_level: int = 0, **kwargs: Any) -> str:
        """Format the given `iterable_value` into a string.

        Args:
            iterable_value (`Iterable`): The iterable to format.
            wrappers (`Tuple[str]`): The start and end characters
                to enclose the iterable.
            use_multiline (`bool`, optional): Whether or not to
                format over multiple lines. Defaults to True.
            indent_level (`int`, optional): The current indent
                level. Defaults to 0.

        Raises:
            TypeError: If the `iterable_value` is not an `iterable`.
            TypeError: If the `wrappers` are not a `tuple`.
            TypeError: If the `use_multiline` is not a `bool`.
            TypeError: If the `indent_level` is not an `int`.

        Returns:
            str: The formatted iterable string.
        """


        if not isinstance(iterable_value, Iterable):
            raise TypeError(f'iterable_value must be of type iterable, got {type(iterable_value)}')

        if not isinstance(wrappers, tuple):
            raise TypeError(f'wrappers must be of type tuple, got {type(wrappers)}')

        if not isinstance(use_multiline, bool):
            raise TypeError(f'use_multiline must be of type bool, got {type(use_multiline)}')

        if not isinstance(indent_level, int):
            raise TypeError(f'indent_level must be of type int, got {type(indent_level)}')

        # Open the wrapper
        text = wrappers[0]

        for index, value in enumerate(iterable_value):
            trail = ''

            if index > 0 or use_multiline:
                trail = ','

            if use_multiline:
                indent_level += 1
                text += f'\n{"\t" * (indent_level + 1)}'

            text += f'{cls.format(value, **kwargs)}{trail}'


        if use_multiline:
            text += f'\n{"\t" * indent_level}'

        # Close the wrapper
        text += wrappers[1]

        return text