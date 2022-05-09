"""Provides logging functionality.

Attributes:
    delimiter (`str`): The delimiter to use for the log message
        between the message and the context, default ' : '
"""

import sys
from typing import Any, Dict, Iterable, List, Set, Tuple


class __Empty__:
    """Class for kwarg default value.

    Note:
        This allows None to be passed and still interpreted
        as a value.
    """


delimiter: str = ' : '


def info(text: str, context: Any = __Empty__):
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
        sys.stdout.write(f'{delimiter}{format(context)}')

    sys.stdout.write('\n')


def log(value: Any, context: Any = __Empty__):
    """Display formatted `value` to the console
    alongside formatted `context`, if passed.

    Args:
        value (`Any`): The information to be formatted and displayed.
        context (`Any`, optional): The value to be formatted and displayed
            along with the `value`. Defaults to __Empty__.
    """

    info(format(value), context)


def label(label: str, context: Any = __Empty__):
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
        sys.stdout.write(format(context))


def exception(error: Exception, reraise: bool = False):
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
        error_message = f'error must be of type Exception, got {type(error)}'

        raise TypeError(error_message)

    label('Exception')
    log(str(error))
    linebreak()

    if reraise:
        raise error


def linebreak(count: int = 1):
    """Display a linebreak to the console.

    Args:
        count (`int`, optional): The number of lines. Defaults to 1.
    """

    sys.stdout.write('\n' * count)


def format(content: Any, **kwargs: Any) -> str:
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
        dict: format_dict,
        list: format_list,
        tuple: format_list,
        set: format_list,
        str: lambda string_value, **kwargs: f'"{str(string_value)}"'
    }

    text = None
    content_type = type(content)

    if content_type in format_methods:
        text = format_methods[content_type](content, **kwargs)

    else:
        text = str(content)

    return text


def format_dict(dict_value: Dict[Any, Any], indent_level: int = 0,
                **kwargs: Any) -> str:
    """Format the given `dict_value` into a string.

    Args:
        dict_value (`Dict[Any, Any]`): The dictionary to format.
        indent_level (`int`, optional): The current indent level. Defaults to
            0.

    Raises:
        TypeError: If the `dict_value` is not a `dict`.
        TypeError: If the `indent_level` is not an `int`.

    Returns:
        `str`: The formatted dictionary string.
    """

    if not isinstance(dict_value, dict):
        error_message = (
            'dict_value must be of type dict, got',
            f'{type(dict_value)}'
        )

        raise TypeError(''.join(error_message))

    if not isinstance(indent_level, int):
        error_message = (
            'indent_level must be of type int, got ',
            f'{type(indent_level)}',
        )

        raise TypeError(''.join(error_message))

    text = '{\n'

    for key, value in dict_value.items():
        current_indent = '\t' * (indent_level + 1)

        formatted_value = format(value, indent_level=indent_level + 1,
                                 **kwargs)

        text += f'{current_indent}"{key}"{delimiter}{formatted_value},\n'

    if text == '{\n':
        text = '\t' * (indent_level - 1) + '{}'

    else:
        text += '\t' * indent_level + '}'

    return text


def format_list(list_value: List[Any], **kwargs: Any) -> str:
    """Format the given `list_value` into a string.

    Args:
        list_value (`List[Any]`): The list to format.

    Raises:
        TypeError: If the `list_value` is not a `list`.

    Returns:
        `str`: The formatted list string.
    """

    if not isinstance(list_value, list):
        error_message = (
            f'list_value must be of type list, got {type(list_value)}',
        )

        raise TypeError(''.join(error_message))

    return format_iterable(list_value, ('[', ']'), **kwargs)


def format_tuple(tuple_value: Tuple[Any], **kwargs: Any) -> str:
    """Format the given `tuple_value` into a string.

    Args:
        tuple_value (`Tuple[Any]`): The tuple to format.

    Raises:
        TypeError: If the `tuple_value` is not a `tuple`.

    Returns:
        `str`: The formatted tuple string.
    """

    if not isinstance(tuple_value, tuple):
        error_message = (
            f'tuple_value must be of type tuple, got {type(tuple_value)}',
        )

        raise TypeError(''.join(error_message))

    return format_iterable(tuple_value, ('(', ')'), **kwargs)


def format_set(set_value: Set[Any], **kwargs: Any) -> str:
    """Format the given `set_value` into a string.

    Args:
        set_value (`Set[Any]`): The set to format.

    Raises:
        TypeError: If the `set_value` is not a `set`.

    Returns:
        `str`: The formatted set string.
    """

    if not isinstance(set_value, set):
        error_message = (
            f'set_value must be of type set, got {type(set_value)}',
        )

        raise TypeError(''.join(error_message))

    return format_iterable(tuple(set_value), ('{', '}'), **kwargs)


def format_iterable(iterable_value: Iterable, wrappers: Tuple[str],
                    use_multiline: bool = True, indent_level: int = 0,
                    **kwargs: Any) -> str:
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
        error_message = (
            'iterable_value must be of type iterable, got ',
            f'{type(iterable_value)}',
        )

        raise TypeError(''.join(error_message))

    if not isinstance(wrappers, tuple):
        error_message = (
            f'wrappers must be of type tuple, got {type(wrappers)}',
        )

        raise TypeError(''.join(error_message))

    if not isinstance(use_multiline, bool):
        error_message = (
            f'use_multiline must be of type bool, got {type(use_multiline)}',
        )

        raise TypeError(''.join(error_message))

    if not isinstance(indent_level, int):
        error_message = (
            f'indent_level must be of type int, got {type(indent_level)}',
        )

        raise TypeError(''.join(error_message))

    # Open the wrapper
    text = wrappers[0]

    for index, value in enumerate(iterable_value):
        trail = ''

        if index > 0 or use_multiline:
            trail = ','

        if use_multiline:
            indent_text = '\t' * (indent_level + 1)
            text += f'\n{indent_text}'

        formatted_value = format(
            value,
            use_multiline=use_multiline,
            indent_level=indent_level + 1,
            **kwargs
        )

        text += f'{formatted_value}{trail}'

    if use_multiline:
        indent_text = '\t' * indent_level
        text += f'\n{indent_text}'

    # Close the wrapper
    text += wrappers[1]

    return text
