"""Parse values into Python objects."""

import operator
from typing import Any, Dict, List, Tuple, Type, Union
from sserver.util import exception


# Maps string operators onto the operator module functions
OPERATOR_MAP = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,
    '%' : operator.mod,
    '**': operator.pow,
}

KEYWORD_MAP = {
    'and': operator.and_,
    'or': operator.or_,
    'not': operator.not_,
}

# Literal syntax map
_LITERAL_SYNTAX_MAP = {
    '"': {
        'value_type': str,
        'escape_char': '\\',
        'end_char': '"',
    },
    "'": {
        'value_type': str,
        'escape_char': '\\',
        'end_char': "'",
    },
    '[': {
        'value_type': list,
        'escape_char': None,
        'end_char': ']',
    },
}


class _Literal:
    """Constructor class for literals."""

    def __new__(cls, char: str, match:
                Dict[str, Union[str, Type, None]]) -> bool:
        """Creates a new literal value.

        Args:
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.

        Returns:
            `_Literal`: The new literal value.

        Raises:
            `UnknownLiteralType`: If the literal type is unknown.
        """

        # Use value type to determine which literal to create
        value_type = match['value_type']

        if value_type == str:
            return _StringLiteral(char, match)
        elif value_type == list:
            return _ListLiteral(char, match)

        raise exception.UnknownLiteralType(
            f'Unknown literal type: {value_type}'
        )


class _BaseLiteral:
    """Represents a literal value."""

    def __init__(self, char: str, match:
                 Dict[str, Union[str, Type, None]]):
        """Initializes the literal value.

        Args:
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.

        Raises:
            `UnknownLiteralType`: If the literal type is unknown.
        """

        self._star_char = char
        self._escape_char = match.get('escape_char')
        self._end_char = match.get('end_char')
        self._value_type = match.get('value_type')

        if self._value_type is None:
            raise exception.UnknownLiteralType(
                f'Unknown literal type: {self._value_type}'
            )

        self._value = char

    def __repr__(self) -> str:
        """Returns the string representation of the literal value.

        Returns:
            `str`: The string representation of the literal value.
        """

        return f'<{self.__class__.__name__}, value: "{self._value}">'

    def append_literal_match(self, char: str, position: int, match:
                             Dict[str, Union[str, Type, None]]
                             ):
        """Appends a literal match to the literal value.

        Args:
            char (`str`): The character to append.
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.
        """

        # Raise a syntax error if append_literal_match is not
        # overridden
        raise exception.ExpressionSyntaxError(
            f'Unexpected literal match: {char} at position {position}'
        )

    def append_character(self, char: str, position: int
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

        # By default, handle appending characters as a string
        previous_character_was_escape = False

        if len(self._value) > 0:
            previous_character_was_escape = (
                self._value[-1] == self._escape_char
            )

        self._value += char

        is_terminated = (
            char == self._end_char
            and previous_character_was_escape
        )

        return is_terminated, True

    def can_terminate(self) -> bool:
        """Returns whether the literal value can be terminated.

        Returns:
            `bool`: Whether the literal value can be terminated.
        """

        return self._end_char == None

    def evaluate(self, context: Dict[str, Any]) -> Any:
        """Evaluates the literal value.

        Args:
            context (`Dict[str, Any]`): The context to evaluate the
                literal value in.

        Returns:
            `Any`: The evaluated literal value.
        """
        
        return self._value_type(self._value)


class _StringLiteral(_BaseLiteral):
    """Represents a string literal value."""

    def append_literal_match(self, char: str, position: int, match:
                             Dict[str, Union[str, Type, None]]
                             ):
        """Appends a literal match to the literal value.

        Args:
            char (`str`): The character to append.
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.
        """

        # Append the character to the string
        self._value += char


class _NumericLiteral(_BaseLiteral):
    """Represents a numeric literal value."""

    def append_character(self, char: str, position: int
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
        super().append_character(char, position)

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

    def evaluate(self, context: Dict[str, Any]) -> Any:
        """Evaluates the literal value.

        Args:
            context (`Dict[str, Any]`): The context to evaluate the
                literal value in.

        Returns:
            `Any`: The evaluated literal value.
        """


class _ListLiteral(_BaseLiteral):
    """Represents a list literal value."""

    def __init__(self, char: str, match:
                 Dict[str, Union[str, Type, None]]):
        """Initializes the literal value.

        Args:
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.

        Raises:
            `UnknownLiteralType`: If the literal type is unknown.
        """

        super().__init__(char, match)

        # Initialize the list value
        self._value = [None]
        self._current_list_literal = None

    def __repr__(self) -> str:
        output = f'<{self.__class__.__name__}, value: ['

        for value in self._value:
            output += f'"{value}", '

        output = output[:-2] + ']>'

        return output

    def append_literal_match(self, char: str, position: int, match:
                             Dict[str, Union[str, Type, None]]
                             ):
        """Appends a literal match to the literal value.

        Args:
            char (`str`): The character to append.
            match (`Dict[str, Union[str, Type, None]]`): The match
                dictionary from character map.
        """

        # If a literal is being parsed in the list, allow it
        # to handle the literal match
        if self._current_list_literal is not None:
            self._current_list_literal.append_literal_match(
                char, position, match
            )

            return

        self._current_list_literal = _Literal(char, match)

    def append_character(self, char: str, position: int
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

        # If a literal is being parsed in the list, allow it
        # to handle the character
        if self._current_list_literal is not None:
            is_terminated, is_consumed = (
                self._current_list_literal.append_character(
                    char, position
                )
            )

            # If the literal is terminated, add it to the list
            # @note is_terminated will never be False if is_consumed
            # is also False
            if is_terminated:
                if self._value[-1] is None:
                    self._value.pop()

                self._value.append(self._current_list_literal)
                self._current_list_literal = None

            if is_consumed:
                return False, is_consumed

        # Check if the character is a list separator or whitespace
        if char == ',':
            # If the character is a list separator, start a new
            # list item
            self._value.append(None)
            return False, True

        # If the character is whitespace, ignore it
        if char.isspace():
            return False, True

        # Check if the character is the end character
        if char == self._end_char:
            # If a literal is being parsed or the last item in the
            # list is not None, a syntax error has occurred
            if (self._current_list_literal is not None):
                raise exception.ExpressionSyntaxError(
                    f'Unexpected syntax: {char} at position {position}'
                )

            # If the last item in the list is None, remove it
            if self._value[-1] is None:
                self._value.pop()

            return True, True

        # If all the above passed, add the character to the current
        # list item
        if self._value[-1] is None:
            self._value[-1] = char

        else:
            self._value[-1] += char

        return False, True


class _Identifier:
    """Represents an identifier."""

    def __init__(self, char: str):
        """Initializes the identifier.

        Args:
            char (`str`): The first character of the identifier.
        """

        self._value = char

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, value: "{self._value}">'

    def append_identifier_character(self, char: str) -> bool:
        """Appends a character to the identifier.

        Args:
            char (`str`): The character to append.

        Returns:
            `bool`: True if the character was appended, False if not.
        """

        next_identifier_value = self._value + char

        # Check if next identifier is valid
        if next_identifier_value.isidentifier():
            self._value = next_identifier_value
            return True

        return False


def string_could_be_operator(string: str) -> bool:
    """Checks if a string could be an operator.

    Args:
        string (`str`): The string to check.

    Returns:
        `bool`: True if the string could be an operator, False if
            not.
    """

    return any(
        operator.startswith(string) for operator in OPERATOR_MAP
    )


def parse_string_to_python(context: Dict[str, Any], args: str
                           ) -> List[Any]:
    """Parse the passed `args` into a list of Python objects.

    Args:
        context (`Dict[str, Any]`): The context variables.
        args (`str`): The argument to parse.

    Returns:
        `List[Any]`: The parsed argument.

    Raises:
        `exception.ExpressionSyntaxError`: Raised when an expression
            syntax error is encountered.
    """
    # @future Support dot notation in template, e.g. if a.b.c == d.e.f
    # @future Parse literals in template, e.g. if a == 1

    parsed_args = []

    current_identifier = None
    current_literal = None

    current_operator = None

    for position, char in enumerate(args):
        if current_operator is not None:
            if string_could_be_operator(current_operator + char):
                current_operator += char
                continue

            # Try to match an operator
            if current_operator in OPERATOR_MAP:
                parsed_args.append(OPERATOR_MAP[current_operator])
                current_operator = None

            else:
                raise exception.ExpressionSyntaxError(
                    f'Unknown operator: {current_operator} at position '
                    f'{position}'
                )

        if char in _LITERAL_SYNTAX_MAP:
            # If an identifier is being parsed, a syntax error has
            # occurred
            if current_identifier is not None:
                raise exception.ExpressionSyntaxError((
                    f'Unexpected literal character: {char} at '
                    f'position {position}'
                ))

            matched_literal = _LITERAL_SYNTAX_MAP[char]

            # If no literal is currently being parsed, start a new one
            if current_literal is None:
                current_literal = _Literal(
                    char,
                    matched_literal,
                )
                continue

            # Combine the matched literal with the current literal
            current_literal.append_literal_match(
                char,
                position,
                matched_literal,
            )

            continue

        # If a literal is currently being parsed, add the character
        # to it
        if current_literal is not None:
            (
                terminated,
                character_consumed,
            ) = current_literal.append_character(char, position)

            if terminated:
                parsed_args.append(current_literal)
                current_literal = None

            if character_consumed:
                continue

        # Check if an identifier is being parsed
        if current_identifier is not None:
            if current_identifier.append_identifier_character(char):
                continue

            else:
                # Identifier is no longer valid, add it to the parsed
                # arguments
                parsed_args.append(current_identifier)
                current_identifier = None

                # Pass to continue parsing current char

        # Next, check for an operator
        if string_could_be_operator(char):
            current_operator = char
            continue

        # If no operator is found, check if the character is a numeric
        if char.isnumeric():
            current_literal = _NumericLiteral(char, {
                'value_type': int,
            })
            continue

        # If the character is a valid identifier character, start a
        # new identifier
        if char.isidentifier():
            current_identifier = _Identifier(char)
            continue

        # If the character is anything other than whitespace, raise
        # syntax error
        if not char.isspace():
            raise exception.ExpressionSyntaxError((
                f'Unexpected character: {char} at position: '
                f'{position}'
            ))

    if current_identifier is not None:
        parsed_args.append(current_identifier)

    if current_literal is not None:
        if not current_literal.can_terminate():
            raise exception.ExpressionSyntaxError((
                'Unexpected end of expression: '
                f'{args}'
            ))

        parsed_args.append(current_literal)

    return parsed_args