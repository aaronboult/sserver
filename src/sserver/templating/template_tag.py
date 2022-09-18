'''Template tags called in templates.'''


import operator
from typing import Any, Dict, List
from sserver.templating.template import Template
from sserver.templating import exception


# Maps string operators onto the operator module functions
_OPERATOR_MAP = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
}


# Decorator to validate the number of arguments passed to a tag
def validate_args_len(expected_len: int, is_block: bool = False):
    '''Decorator to validate the number of arguments passed to a tag.

    Args:
        expected_len (`int`): The expected number of arguments.
        is_block (`bool`): Whether the tag is a block tag.

    Returns:
        `Callable`: The decorator.
    '''

    def decorator(func):
        # Two functions are generated here for better error messages
        # when required positional arguments are missing
        if is_block:
            def wrapper(context, block_contents, *args):
                _validate_args_len(func.__name__, args, expected_len)

                return func(context, block_contents, *args)

        else:
            def wrapper(context, *args):
                _validate_args_len(func.__name__, args, expected_len)

                return func(context, *args)

        return wrapper
    return decorator


def _validate_args_len(tag_name: str, args: List[str], expected_len: int) -> bool:
    '''Validates the length of the arguments passed to a tag.

    Args:
        tag_name (`str`): The name of the tag.
        args (`List[str]`): The arguments passed to the tag.
        expected_len (`int`): The expected length of the arguments.

    Raises:
        `TooManyTagArgumentsException`: If the number of arguments
            passed to the tag is greater than the expected length.

        `MissingTagArgumentsException`: If the number of arguments
            passed to the tag is less than the expected length.

    Returns:
        `bool`: True if the arguments are valid, an exception is
            raised otherwise.
    '''

    args_len = len(args)

    if args_len > expected_len:
        raise exception.TooManyTagArgumentsException(
            (
                f'Too many arguments passed to {tag_name} tag. ',
                f'Expected {expected_len} arguments, got {args_len}.'
            )
        )

    if args_len < expected_len:
        raise exception.MissingTagArgumentsException(
            (
                f'Missing arguments passed to {tag_name} tag. ',
                f'Expected {expected_len} arguments, got {args_len}.'
            )
        )

    return True


def parse_args(context: Dict[str, Any], args: List[str]) -> List[Any]:
    '''Parses the arguments passed to a tag.

    Args:
        args (`List[str]`): The arguments passed to the tag.

    Returns:
        `List[Any]`: The parsed arguments.
    '''

    # @future Support dot notation in template, e.g. if a.b.c == d.e.f
    # @future Parse literals in template, e.g. if a == 1

    return args


@validate_args_len(1)
def include(*args) -> str:
    '''Includes a template.

    Args:
        *args (`str`): Arguments passed to the tag.

    Note:
        Expects len(args) == 1 and args[0] to be the template to
            import.
    '''

    template_to_include = Template(args[0]).template_str

    if template_to_include is None:
        template_to_include = ''

    return template_to_include


@validate_args_len(3, is_block=True)
def if_block(context: Dict[str, Any], block_contents: str, *args
             ) -> str:
    '''Renders a conditional if statement.

    Args:
        context (`Dict[str, Any]`): The context to render the block
            with.
        block_contents (`str`): The contents of the block.
        *args (`str`): Arguments passed to the tag.

    Note:
        Expects args[0] and args[2] to be the left and right operands,
            respectively, and args[1] to be the operator.

    Raises:
        `UnknownTagConditionalExpressionException`: If the conditional
            expression is not recognized.

    Returns:
        `str`: The rendered block.
    '''

    left_expression = args[0]
    operator = args[1]
    right_expression = args[2]

    if left_expression in context:
        left_expression = context[left_expression]

    if right_expression in context:
        right_expression = context[right_expression]

    if operator not in _OPERATOR_MAP:
        raise exception.UnknownTagConditionalExpressionException(
            f'Unknown operator {operator}'
        )

    conditional_output = _OPERATOR_MAP[operator](
        left_expression,
        right_expression
    )

    if conditional_output:
        return block_contents

    return ''


@validate_args_len(0, is_block=True)
def for_block(context: Dict[str, Any], block_contents: str, *args
              ) -> str:
    '''Renders a for loop.

    Args:
        context (`Dict[str, Any]`): The context to render the block
            with.
        block_contents (`str`): The contents of the block.
        *args (`str`): Arguments passed to the tag.

    Returns:
        `str`: The rendered block.
    '''

    output = ''

    for i in range(5):
        output += block_contents

    return output
