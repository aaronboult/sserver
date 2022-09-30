"""Template tags called in templates."""


from typing import List
from sserver.templating import exception


# Decorator to validate the number of arguments passed to a tag
def validate_args_len(tag_name: str, args: List[str], expected_len:
                      int) -> bool:
    """Validates the length of the arguments passed to a tag.

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
    """

    args_len = len(args)

    # Ensure args_len is an int
    if not isinstance(expected_len, int):
        raise TypeError((
            'Expected length must be an int. '
            f'Got {type(expected_len)} instead.'
        ))

    if args_len > expected_len:
        raise exception.TooManyTagArgumentsException(
            (
                f'Too many arguments passed to {tag_name} tag. '
                f'Expected {expected_len} arguments, got {args_len}.'
            )
        )

    if args_len < expected_len:
        raise exception.MissingTagArgumentsException(
            (
                f'Missing arguments passed to {tag_name} tag. '
                f'Expected {expected_len} arguments, got {args_len}.'
            )
        )

    return True
