"""Literal class declarations."""


from typing import Any, List, Tuple
from sserver.parse.parse import (
    Expression,
    parse_string_to_value,
    exception,
)
from sserver.parse.base_literal import (
    Evaluatable,
    Operator,
    BaseLiteral,
    EnclosingLiteral,
    NumericLiteral,
    get_constant_operator_map,
    add_constant_operator,
    try_add_constant_operator,
    get_literal_syntax_map,
    is_unterminated_literal,
    register_literal_class,
    create_literal,
    Context,
    LiteralMatch,
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

# Expose literal classes and functions
__all__ = [
    'Expression',
    'Evaluatable',
    'Operator',
    'BaseLiteral',
    'EnclosingLiteral',
    'NumericLiteral',
    'StringLiteral',
    'ListLiteral',
    'ParenthesisLiteral',
    'parse_string_to_value',
    'get_constant_operator_map',
    'add_constant_operator',
    'try_add_constant_operator',
    'get_literal_syntax_map',
    'is_unterminated_literal',
    'register_literal_class',
    'create_literal',
    'Context',
    'LiteralMatch',
]