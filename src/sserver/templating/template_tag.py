"""Template tags called in templates."""


from typing import List, Optional
from sserver.templating import (
    register_inline_tag,
    register_block_tag,
    Template,
    TemplateRenderer,
    BlockTagContents,
    exception,
)
from sserver.parse import (
    parse_string_to_value,
    parse_string_to_expression,
    Identifier,
    Context,
)


# Function to validate the number of arguments passed to a tag
def validate_args_len(tag_name: str, args: List[str], expected_len:
                      int) -> bool:
    """Validates the length of the arguments passed to a tag.

    Args:
        tag_name (`str`): The name of the tag.
        args (`List[str]`): The arguments passed to the tag.
        expected_len (`int`): The expected length of the arguments.

    Raises:
        `TypeError`: If `expected_len` is not an `int`.
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


@register_inline_tag('include')
def include(context: Context, args) -> str:
    """Includes a template.

    Args:
        *args (`str`): Arguments passed to the tag.

    Note:
        Excepts a single string after parsing arguments.

    Raises:
        `TemplateArgumentException`: If the argument passed is not a
            string.
    """

    # Parse the arguments
    arg_value = parse_string_to_value(context, args)

    if not isinstance(arg_value, str):
        raise exception.TemplateArgumentException(
            'include tag expects a single string argument'
        )

    template_to_include = Template(arg_value).template_str

    if template_to_include is None:
        template_to_include = ''

    return template_to_include


@register_inline_tag('parse')
def parse(context: Context, args) -> str:
    """Parses a string.

    Args:
        *args (`str`): Arguments passed to the tag.

    Note:
        Excepts a single string after parsing arguments.

    Raises:
        `TemplateArgumentException`: If the argument passed is not a
            string.
    """

    # Parse the arguments
    return str(parse_string_to_value(context, args))


@register_block_tag(
    tag_name='if',
    end_tag='endif',
    sub_tag_list=[
        'elif',
        'else',
    ]
)
def conditional_block(context: Context, block_contents:
                      BlockTagContents, args) -> Optional[str]:
    """Renders a conditional if statement.

    Args:
        context (`Context`): The context to render the block
            with.
        block_contents (`_TagLogicBlockContents`): The contents of the
            block.
        *args (`str`): Arguments passed to the tag.

    Note:
        Expects a single boolean value after parsing arguments.

    Returns:
        `str`: The rendered block.
    """

    # Parse the arguments
    conditional_output = parse_string_to_value(context, args)

    if conditional_output is True or conditional_output is None:
        return block_contents

    return None


@register_block_tag(
    tag_name='for',
    end_tag='endfor',
)
def for_block(context: Context, block_contents:
              BlockTagContents, args) -> str:
    """Renders a for loop.

    Note:
        Expects exactly three arguments after parsing arguments.
            The first argument being an identifier to assign the
            current iteration to, the third argument being the
            iterable to iterate over.

    Args:
        context (`Context`): The context to render the block
            with.
        block_contents (`_TagLogicBlockContents`): The contents of the
            block.
        *args (`str`): Arguments passed to the tag.

    Returns:
        `str`: The rendered block.

    Raises:
        `TemplateArgumentException`: If the first argument is not a
            valid identifier or if the third argument is not a valid
            iterable.
    """

    # Parse the arguments
    args = parse_string_to_expression(args)

    validate_args_len('for', args, 3)

    # Extract the identifier and iterable
    identifier = args[0]
    iterable = args[2].evaluate(context)

    # Ensure identifier and iterable are of correct type
    if not isinstance(identifier, Identifier):
        raise exception.TemplateArgumentException(
            'for tag expects identifier as first argument'
        )

    if not hasattr(iterable, '__iter__'):
        raise exception.TemplateArgumentException(
            'for tag expects iterable as third argument'
        )

    output = ''

    for item in iterable:
        template = Template()
        template.set_template_str(block_contents)

        renderer = TemplateRenderer(template)

        output += renderer.render({
            **context,
            identifier.name: item,
        })

    return output
