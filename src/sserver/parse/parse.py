"""Parse values into Python objects."""

from typing import Any, Optional, Union
from sserver.parse.base_literal import (
    Evaluatable,
    BaseLiteral,
    Operator,
    NumericLiteral,
    get_literal_syntax_map,
    create_literal,
    Context,
)
from sserver.parse.parse_tree import Expression
from sserver.parse import exception


class Identifier(Evaluatable):
    """Represents an identifier."""

    def __init__(self, char: str):
        """Initializes the identifier.

        Args:
            char (`str`): The first character of the identifier.
        """

        self._value = char
        self._child_identifier = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, value: "{self._value}">'

    @property
    def name(self) -> str:
        """`str`: The name of the identifier."""

        return self._value

    def append_identifier_character(self, char: str) -> bool:
        """Appends a character to the identifier.

        Args:
            char (`str`): The character to append.

        Returns:
            `bool`: True if the character was appended, False if not.
        """

        # If the attribute identifier is not None, append the
        # character to it
        if self._child_identifier is not None:
            return self._child_identifier.append_identifier_character(
                char
            )

        # If the character is a ".", start an attribute identifier
        if char == '.':
            self._child_identifier = Identifier('')
            return True

        next_identifier_value = self._value + char

        # Check if next identifier is valid
        if next_identifier_value.isidentifier():
            self._value = next_identifier_value
            return True

        return False

    def evaluate(self, context: Context
                 ) -> Optional[Union[Any, callable]]:
        """Evaluates the identifier. Returns None if no value found
            in context.

        Args:
            context (`Context`): The context variables.

        Returns:
            `Any | callable`: The value of the identifier or the
                keywords function.
        """

        value = None

        if self._value in context:
            if hasattr(context, '__getitem__'):
                value = context[self._value]

                if self._child_identifier is not None:
                    value = self._child_identifier.evaluate(value)

        return value


def parse_string_to_expression(args: str):
    """Parse the passed `args` string into a list of Python objects.

    Args:
        args (`str`): The arguments to parse.

    Returns:
        `List[Any]`: The parsed argument.

    Raises:
        `ExpressionSyntaxError`: Raised when an unexpected operator or
            character is encountered.
    """

    parsed_args = []

    current_identifier: Identifier = None
    current_literal: BaseLiteral = None

    current_operator: str = None

    for position, char in enumerate(args):
        if current_operator is not None:
            # Check if appending the current character leads to an
            # operator
            if Operator.string_could_be_operator(
                        current_operator + char
                    ):
                current_operator += char
                continue

            # If the current character marks the end of an operator,
            # add the operator to the parsed arguments if it is valid
            if Operator.is_valid_operator(current_operator):
                parsed_args.append(
                    Operator(current_operator)
                )
                current_operator = None

            # If the current operator is not valid, check if it could
            # be an identifier (e.g 'an' with char 't' is an
            # identifier and not the keyword 'and')
            elif (current_operator + char).isidentifier():
                current_identifier = Identifier(
                    current_operator + char
                )
                current_operator = None
                continue

            # If adding the current character does not lead to a valid
            # identifier, check if not adding the current character
            # leads to a valid identifier
            elif current_operator.isidentifier():
                parsed_args.append(
                    Identifier(current_operator)
                )
                current_operator = None

            else:
                raise exception.ExpressionSyntaxException(
                    f'Unknown operator: {current_operator} at position '
                    f'{position}'
                )

        LITERAL_SYNTAX_MAP = get_literal_syntax_map()

        if char in LITERAL_SYNTAX_MAP:
            # If an identifier is being parsed, a syntax error has
            # occurred
            if current_identifier is not None:
                raise exception.ExpressionSyntaxException((
                    f'Unexpected literal character: {char} at '
                    f'position {position}'
                ))

            matched_literal = LITERAL_SYNTAX_MAP[char]

            # If no literal is currently being parsed, start a new one
            if current_literal is None:
                current_literal = create_literal(
                    char,
                    matched_literal,
                )
                continue

            # Combine the matched literal with the current literal
            terminated = current_literal._append_literal_match(
                char,
                position,
                matched_literal,
            )

            # If the literal has been terminated, evaluate and add to
            # parsed args
            if terminated:
                parsed_args.append(
                    current_literal
                )

                current_literal = None

            continue

        # If a literal is currently being parsed, add the character
        # to it

        if current_literal is not None:
            (
                terminated,
                character_consumed,
            ) = current_literal._append_character(char, position)

            # If the literal has been terminated, evaluate and add to
            # parsed args
            if terminated:
                parsed_args.append(
                    current_literal
                )
                current_literal = None

            if character_consumed:
                continue

        # Check if an identifier is being parsed
        if current_identifier is not None:
            if current_identifier.append_identifier_character(char):
                continue

            else:
                # Identifier is no longer valid, evaluate and add to
                # parsed args
                parsed_args.append(
                    current_identifier
                )
                current_identifier = None

                # Pass to continue parsing current char

        # Next, check for an operator
        if Operator.string_could_be_operator(char):
            current_operator = char
            continue

        # If no operator is found, check if the character is a numeric
        if char.isnumeric():
            current_literal = NumericLiteral(char)
            continue

        # If the character is a valid identifier character, start a
        # new identifier
        if char.isidentifier():
            current_identifier = Identifier(char)
            continue

        # If the character is anything other than whitespace, raise
        # syntax error
        if not char.isspace():
            raise exception.ExpressionSyntaxException((
                f'Unexpected character: {char} at position: '
                f'{position}'
            ))

    # If parsing concluded with an operator in progress, check if it
    # is a valid operator or identifier
    if current_operator is not None:
        if Operator.is_valid_operator(current_operator):
            parsed_args.append(
                Operator(current_operator)
            )

        elif current_operator.isidentifier():
            parsed_args.append(
                Identifier(current_operator)
            )
        else:
            raise exception.ExpressionSyntaxException((
                f'Unknown operator: {current_operator}'
            ))

    # If parsing concluded with an identifier in progress, evaluate
    # it and add to parsed args
    if current_identifier is not None:
        parsed_args.append(
            current_identifier
        )

    # If parsing concluded with a literal in progress, evaluate it
    # and add to parsed args
    if current_literal is not None:
        if not current_literal._can_terminate():
            raise exception.ExpressionSyntaxException((
                'Unexpected end of expression: '
                f'{args}'
            ))

        parsed_args.append(
            current_literal
        )

    return Expression(parsed_args)


def parse_string_to_value(context: Context, args: str
                          ) -> Optional[Any]:
    """Parse the passed `args`string  into a value.

    Args:
        context (`Context`): The context variables.
        args (`str`): The arguments to parse.

    Returns:
        `Any`: The parsed value. If the value is empty, `None` is
            returned.
    """

    parsed_expression = parse_string_to_expression(args)

    return parsed_expression.evaluate(context)
