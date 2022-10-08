"""Parse values into Python objects."""
# @future Allow imports like: from sserver.parse import ... instead
# of from sserver.parse.parse import ...

from typing import Any, List, Optional, Tuple, Union
from sserver.parse.parse_tree import Expression
from sserver.parse import exception
from sserver.parse.literal import (
    BaseLiteral,
    Evaluatable,
    Operator,
    create_literal,
    register_literal_class,
    is_unterminated_literal,
    get_literal_syntax_map,
    LiteralMatch,
    Context,
)


@register_literal_class(
    start_char=('"', '\''),
    end_char=('"', '\''),
    value_type=str,
    escape_char='\\',
)
class StringLiteral(BaseLiteral):
    """Represents a string literal value."""

    def _append_literal_match(self, char: str, position: int, match:
                              LiteralMatch
                              ):
        """Appends a literal match to the literal value.

        Args:
            char (`str`): The character to append.
            match (`LiteralMatch`): The match
                dictionary from character map.

        Returns:
            `bool`: Whether the literal value is complete.
        """

        if self._is_end_char(char):
            return True

        self._try_strip_escape_char(char)
        self._value += char

        return False


class NumericLiteral(BaseLiteral):
    """Represents a numeric literal value."""

    def __init__(self, char: str):
        match = {
            'value_type': (int, float),
        }

        super().__init__(char, match)

        # Append the character to the string
        self._value += char

    def _append_character(self, char: str, position: int
                          ) -> Tuple[bool, bool]:
        """Appends a character to the literal value.

        Args:
            char (`str`): The character to append.
            position (`int`): The position of the character in the
                expression.

        Returns:
            `Tuple[bool, bool]`: A tuple containing a boolean
                indicating whether the literal value is complete and
                a boolean indicating whether the character has been
                consumed by the literal value.
        """

        # Append the value as a string
        super()._append_character(char, position)

        # Check the value is still numeric
        try:
            float(self._value)
            return False, True

        except ValueError:
            pass

        # If the value is no longer numeric, remove the last
        # character and return
        self._value = self._value[:-1]

        return True, False


class EnclosingLiteral(BaseLiteral):
    """Represents a literal that encloses a value or values."""

    def _append_literal_match(self, char: str, position: int, match:
                              LiteralMatch
                              ):
        """Appends a literal match to the literal value.

        Note:
            List literals do not have an end character that matches
                another literals start character, so this should
                always return False.

        Args:
            char (`str`): The character to append.
            match (`LiteralMatch`): The match
                dictionary from character map.
        """

        # Append the character normally
        return self._append_character(char, position)[0]

    def _char_terminates_literal(self, char: str, value: str) -> bool:
        """Checks if a character terminates the enclosing literal.

        Note:
            Value is passed as a variable instead of using
                `self._value` to allow

        Args:
            char (`str`): The character to check.
            value (`str`): The value to check.

        Returns:
            `bool`: Whether the character terminates the literal.
        """

        # Check if the character is the end character
        if char == self._end_char:
            # Return whether the value is an unterminated literal
            return not is_unterminated_literal(value)

        return False


@register_literal_class(
    start_char='[',
    end_char=']',
    value_type=list
)
class ListLiteral(EnclosingLiteral):
    """Represents a list literal value."""

    def __init__(self, char: str, match:
                 LiteralMatch):

        super().__init__(char, match)

        # Initialize the list value
        self._value = [None]

    def __repr__(self) -> str:
        output = f'<{self.__class__.__name__}, value: ['

        for value in self._value:
            if value is not None:
                output += f'{value}, '

        output = output[:-2] + ']>'

        return output

    def _append_character(self, char: str, position: int
                          ) -> Tuple[bool, bool]:
        """Appends a character to the literal value.

        Args:
            char (`str`): The character to append.
            position (`int`): The position of the character in the
                expression.

        Returns:
            `Tuple[bool, bool]`: A tuple containing a boolean
                indicating whether the literal value is complete and
                a boolean indicating whether the character has been
                consumed by the literal value.
        """

        # Check if the character is a list separator or whitespace
        if char == ',':
            self._value.append(None)
            return False, True

        previous_value = self._value[-1]

        # Only ignore whitespace if it comes after a list separator
        # or the start of the list
        if char.isspace() and previous_value is None:
            return False, True

        if self._char_terminates_literal(char, previous_value):
            # If the last item in the list is None, remove it
            if previous_value is None:
                self._value.pop()

            return True, True

        # If all the above passed, add the character to the current
        # list item
        if previous_value is None:
            self._value[-1] = char

        else:
            self._value[-1] += char

        return False, True

    def evaluate(self, context: Context) -> List[Any]:
        """Evaluates the list literal value.

        Args:
            context (`Context`): The context dictionary.

        Returns:
            `List[Any]`: The evaluated list literal value.

        Raises:
            `ExpressionSyntaxException`: If the list literal
                encounters an unexpected separator character.
        """

        # Evaluate the list by parsing the strings of each item
        evaluated_list = []
        for index, value in enumerate(self._value):
            # If the value is None, a syntax error has occurred
            if value is None:
                # Generate list string for error message and replace
                # None with ""

                exception_list_string = str(self._value).replace(
                    'None',
                    ''
                )

                raise exception.ExpressionSyntaxException(
                    f'Unexpected list separator between list index '
                    f'{index - 1} and list index {index} in list: '
                    f'{exception_list_string}'
                )

            # Parse the item string
            parsed_value = parse_string_to_value(context, value)

            evaluated_list.append(parsed_value)

        return evaluated_list


@register_literal_class(
    start_char='(',
    end_char=')',
    value_type=Expression
)
class ParenthesisLiteral(EnclosingLiteral):
    """Represents a parenthesized literal."""

    def _append_character(self, char: str, position: int
                          ) -> Tuple[bool, bool]:
        # Check if the character terminates the literal
        # Add an additional "(" to the value to account for the
        # open parenthesis that is not included in the value
        if self._char_terminates_literal(char, self._value):
            return True, True

        # Append the character normally
        self._value += char

        return False, True

    def evaluate(self, context: Context) -> Any:
        return parse_string_to_value(context, self._value)


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


def parse_string_to_object_list(args: str):
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

    parsed_expression = parse_string_to_object_list(args)

    return parsed_expression.evaluate(context)
