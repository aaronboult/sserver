"""Definitions and functions for literal object handling."""


import math
import inspect
import operator
from typing import Any, Dict, Optional, Tuple, Type, Union
from sserver.util import log
from sserver.parse import exception


# Maps string operators onto the operator module functions
CONSTANT_OPERATOR_MAP = {
    'pi': {
        'function': lambda: math.pi,
    },
}

CONSTANT_OPERATOR_PRECEDENCE = 8

ARITHMETIC_OPERATOR_MAP = {
    '+' : {
        'function': operator.add,
        'precedence': 5,
    },
    '-' : {
        'function': operator.sub,
        'precedence': 5,
    },
    '*' : {
        'function': operator.mul,
        'precedence': 6,
    },
    '/' : {
        'function': operator.truediv,
        'precedence': 6,
    },
    '//': {
        'function': operator.floordiv,
        'precedence': 6,
    },
    '%' : {
        'function': operator.mod,
        'precedence': 6,
    },
    '**': {
        'function': operator.pow,
        'precedence': 7,
    },
}

LOGICAL_OPERATOR_MAP = {
    '==': {
        'function': operator.eq,
    },
    '!=': {
        'function': operator.ne,
    },
    '>': {
        'function': operator.gt,
    },
    '>=': {
        'function': operator.ge,
    },
    '<': {
        'function': operator.lt,
    },
    '<=': {
        'function': operator.le,
    },
    'in': {
        'function': lambda x, y: x in y,
    }
}

LOGICAL_OPERATOR_PRECEDENCE = 4

KEYWORD_OPERATOR_MAP = {
    'not': {
        'function': operator.not_,
        'precedence': 3,
    },
    'and': {
        'function': operator.and_,
        'precedence': 2,
    },
    'or': {
        'function': operator.or_,
        'precedence': 1,
    },
}

VALID_OPERATOR_CHARS = (
    list(ARITHMETIC_OPERATOR_MAP.keys()) +
    list(CONSTANT_OPERATOR_MAP.keys()) +
    list(LOGICAL_OPERATOR_MAP.keys()) +
    list(KEYWORD_OPERATOR_MAP.keys())
)


# Literal syntax map
_literal_syntax_map = {
    # '"': {
    #     'value_type': str,
    #     'escape_char': '\\',
    #     'end_char': '"',
    #     'literal_class': StringLiteral,
    # },
    # '\'': {
    #     'value_type': str,
    #     'escape_char': '\\',
    #     'end_char': '\'',
    #     'literal_class': StringLiteral,
    # },
    # '[': {
    #     'value_type': list,
    #     'escape_char': None,
    #     'end_char': ']',
    #     'literal_class': ListLiteral,
    # },
    # '(' : {
    #     'value_type': Expression,
    #     'escape_char': None,
    #     'end_char': ')',
    #     'literal_class': ParenthesisLiteral,
    # },
}


# Alias for literal match
LiteralMatch = Dict[str, Union[str, Type, None]]

# Alias for context
Context = Dict[str, Any]


# Getter for literal syntax map
def get_literal_syntax_map() -> Dict[str, LiteralMatch]:
    """The literal syntax map.

    Returns:
        `Dict[str, LiteralMatch]`: The literal syntax map.
    """

    return _literal_syntax_map


def _register_literal_class(literal_class: Type,
                            start_char: Union[str, Tuple[str]],
                            value_type: Type,
                            end_char: Optional[str],
                            escape_char: Optional[str]):
    """Registers a literal class to be used when parsing.

    Args:
        char (`str`): The character that starts the literal.
        value_type (`Type`): The type of the literal value.
        literal_class (`Type`): The literal class.
        end_char (`Optional[str]`): The character that ends the literal.
            Defaults to `None`.
        escape_char (`Optional[str]`): The character that escapes the
            end character. Defaults to `None`.

    Raises:
        `ValueError`: If the literal class passed is not a subclass
            or `BaseLiteral`.
        `LiteralCharacterAlreadyInUseException`: If the literal
            character is already in use.
    """

    if not issubclass(literal_class, BaseLiteral):
        raise ValueError(
            f'Literal class {literal_class.__name__} must '
            'be a subclass of BaseLiteral'
        )

    if start_char in _literal_syntax_map:
        raise exception.LiteralCharacterAlreadyInUseException(
            f'Character "{start_char}" is already in use'
        )

    _literal_syntax_map[start_char] = {
        'value_type': value_type,
        'escape_char': escape_char,
        'end_char': end_char,
        'literal_class': literal_class,
    }


# Decorator for literal classes to register them
def register_literal_class(start_char: Union[str, Tuple[str]],
                           value_type: Type,
                           end_char: Optional[str] = None,
                           escape_char: Optional[str] = None,
                           ) -> callable:
    """Decorator for registering a literal class to be used when
        parsing.

    Args:
        char (`str`): The character that starts the literal.
        value_type (`Type`): The type of the literal value.
        end_char (`Optional[str]`): The character that ends the literal.
            Defaults to `None`.
        escape_char (`Optional[str]`): The character that escapes the
            end character. Defaults to `None`.

    Returns:
        `callable`: The decorator function.

    Raises:
        `ValueError`: If start character and end character are not of
            the same type, or if both start character and end
            character are passed as tuples and have different lengths,
            or if the start character is not a string or tuple of
            strings.
    """
    def decorator(cls):
        """The decorator function."""

        if type(start_char) != type(end_char):
            raise ValueError(
                'char and end_char must be of the same type'
            )

        if isinstance(start_char, tuple):
            if not isinstance(end_char, tuple):
                raise ValueError(
                    'end_char must be a tuple if char is a tuple and '
                    'must have equal length'
                )

            if len(start_char) != len(end_char):
                raise ValueError(
                    'char and end_char must have equal length if '
                    'either are passed as a tuple'
                )

            for character, end_character in zip(start_char, end_char):
                _register_literal_class(
                    cls,
                    character,
                    value_type,
                    end_character,
                    escape_char
                )

        elif not isinstance(start_char, str):
            raise ValueError(
                'char must be a string or a tuple of strings'
            )

        elif end_char is not None and not isinstance(end_char, str):
            raise ValueError(
                'end_char must be a string or a tuple of strings '
                'and must be of the same type as char (with '
                'equal length is char is a tuple)'
            )

        else:
            _register_literal_class(
                cls,
                start_char,
                value_type,
                end_char,
                escape_char
            )

        return cls

    return decorator


class Evaluatable:
    """Represents an evaluatable object."""

    def evaluate(self, context: Context) -> Any:
        """Evaluates the object.

        Args:
            context (`Context`): The context to evaluate the object in.

        Returns:
            `Any`: The evaluated object.

        Raises:
            `NotImplementedError`: If the method is not implemented by
                the subclass.
        """

        raise NotImplementedError((
            'Evaluate not implemented for '
            f'{self.__class__.__name__}'
        ))


class BaseLiteral(Evaluatable):
    """Represents a literal value."""

    def __init__(self, char: str, match:
                 LiteralMatch):
        """Initializes the literal value.

        Args:
            match (`LiteralMatch`): The match
                dictionary from character map.

        Raises:
            `UnknownLiteralType`: If the literal type is unknown.
        """

        self._star_char = char
        self._escape_char = match.get('escape_char')
        self._end_char = match.get('end_char')
        self._value_type = match.get('value_type')

        if self._value_type is None:
            raise exception.UnknownLiteralTypeException(
                f'Unknown literal type: {self._value_type}'
            )

        self._value = ''

    def __repr__(self) -> str:
        """Returns the string representation of the literal value.

        Returns:
            `str`: The string representation of the literal value.
        """

        return f'<{self.__class__.__name__}, value: {self._value}>'

    def _append_literal_match(self, char: str, position: int, match:
                             LiteralMatch
                             ) -> bool:
        """Appends a literal match to the literal value.

        Note:
            Literal characters passed are considered to always
                be consumed as they are either appended or are the
                end character.

        Args:
            char (`str`): The character to append.
            match (`LiteralMatch`): The match
                dictionary from character map.

        Returns:
            `bool`: Whether the literal value is complete.

        Raises:
            `ExpressionSyntaxException`: If a literal character is
                matched at an unexpected position.
        """

        # Raise a syntax error if append_literal_match is not
        # overridden
        raise exception.ExpressionSyntaxException(
            f'Unexpected literal match: {char} at position {position}'
        )

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

        if self._is_end_char(char):
            return True, True

        self._try_strip_escape_char(char)
        self._value += char

        return False, True

    def _previous_char_was_escape(self) -> bool:
        """Returns whether the previous character was an escape
        character.

        Returns:
            `bool`: Whether the previous character was an escape
                character.
        """

        # By default, handle appending characters as a string
        previous_char_was_escape = False

        if len(self._value) > 0:
            previous_char_was_escape = (
                self._value[-1] == self._escape_char
            )

        return previous_char_was_escape

    def _is_end_char(self, char: str):
        """Checks if `char` is a valid end to the literal.

        Args:
            char (`str`): The character to check.

        Returns:
            `bool`: Whether the character is a valid end to the
                literal.
        """

        return (
            char == self._end_char
            and not self._previous_char_was_escape()
        )

    def _try_strip_escape_char(self, char: str):
        """Strips the escape character from a character if it is
        present.

        Args:
            char (`str`): The current character.
        """

        # By default, handle appending characters as a string
        previous_char_was_escape = self._previous_char_was_escape()

        is_end_char = char == self._end_char

        # Strip the escape character from the value if the end
        # character is met after an escape character
        if is_end_char and previous_char_was_escape:
            self._value = self._value[:-1]

    def _can_terminate(self) -> bool:
        """Returns whether the literal value can be terminated.

        Note:
            This method determines if the literal value can be
                immediately terminated.

        Returns:
            `bool`: Whether the literal value can be terminated.
        """

        return self._end_char is None

    def evaluate(self, context: Context) -> Any:
        """Evaluates the literal value.

        Args:
            context (`Context`): The context to evaluate the
                literal value in.

        Returns:
            `Any`: The evaluated literal value.

        Raises:
            `ExpressionSyntaxException`: If the literal value failed
                to be cast to its value type.
        """

        # If value_type is a tuple, try each type and the first that
        # succeeds is the value type
        if isinstance(self._value_type, tuple):
            for value_type in self._value_type:
                try:
                    return value_type(self._value)
                except ValueError:
                    pass

            raise exception.ExpressionSyntaxException(
                f'Invalid literal value: {self._value}'
            )

        return self._value_type(self._value)


class Operator:
    """Represents an arithmetic or logical operator."""

    def __init__(self, char: str):
        '''Initializes the operator.

        Raises:
            `UnknownOperatorException`: If the operator is unknown.
        '''

        if char not in VALID_OPERATOR_CHARS:
            raise exception.UnknownOperatorException(
                f'Unknown operator: {char}'
            )

        self._operator = char

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__name__}, '
            f'operator: "{self._operator}">'
        )

    def __call__(self, *args):
        '''Calls the operator function.'''

        func = self._get_function()

        return func(*args)

    def _get_operator_map_match(self) -> LiteralMatch:
        '''Gets the respective operators match.

        Returns:
            `LiteralMatch`: The operators respecive match.

        Raises:
            `UnknownOperatorException`: If the operator is unknown.
        '''

        match = None

        if self._operator in ARITHMETIC_OPERATOR_MAP:
            match = ARITHMETIC_OPERATOR_MAP[self._operator]

        elif self._operator in CONSTANT_OPERATOR_MAP:
            match = CONSTANT_OPERATOR_MAP[self._operator]

        elif self._operator in LOGICAL_OPERATOR_MAP:
            match = LOGICAL_OPERATOR_MAP[self._operator]

        elif self._operator in KEYWORD_OPERATOR_MAP:
            match = KEYWORD_OPERATOR_MAP[self._operator]

        # Check a match was found
        if match is None:
            raise exception.UnknownOperatorException(
                f'Unknown operator: {self._operator}'
            )

        return match

    def _get_function(self) -> callable:
        '''Gets the operator function.

        Returns:
            `callable`: The operator function.
        '''

        match = self._get_operator_map_match()
        func = match.get('function')

        if func is None:
            raise exception.MissingOperatorFunctionException(
                f'Missing operator function: {self._operator}'
            )

        return func

    @classmethod
    def is_valid_operator(cls, char: str) -> bool:
        """Checks if the character is a valid operator.

        Args:
            char (`str`): The character to check.

        Returns:
            `bool`: True if the character is a valid operator, False
                if not.
        """

        return char in VALID_OPERATOR_CHARS

    @classmethod
    def string_could_be_operator(cls, string: str) -> bool:
        """Checks if the string could be an operator.

        Args:
            string (`str`): The string to check.

        Returns:
            `bool`: True if the string could be an operator, False if
                not.
        """

        return any(
            operator.startswith(string)
            for operator in VALID_OPERATOR_CHARS
        )

    @property
    def precedence(self) -> int:
        """Gets the operators precedence.

        Returns:
            `int`: The operators precedence.

        Raises:
            `UnknownOperatorException`: If the operator is unknown.
        """

        if self._operator in LOGICAL_OPERATOR_MAP:
            return LOGICAL_OPERATOR_PRECEDENCE

        elif self._operator in CONSTANT_OPERATOR_MAP:
            return CONSTANT_OPERATOR_PRECEDENCE

        match = self._get_operator_map_match()

        precedence = match.get('precedence')

        if precedence is None:
            raise exception.MissingOperatorPrecedenceException(
                f'Missing operator precedence: {self._operator}'
            )

        return precedence

    @property
    def argument_count(self) -> int:
        """Gets the number of arguments the operator takes.

        Returns:
            `int`: The number of arguments the operator takes.
        """

        func = self._get_function()

        return len(inspect.signature(func).parameters)


def is_unterminated_literal(value: str) -> bool:
    """Returns whether the value is an unterminated literal.

    Args:
        value (`str`): The string value to check.

    Returns:
        `bool`: Whether the value is unterminated.

    Raises:
        `ExpressionSyntaxException`: If a literal close character is
            encountered without an open character.
    """

    # If one or less characters present, the value cannot be
    # terminated
    if len(value) <= 1:
        return False

    # Keep track of all open literals
    # Create mappings for open and close characters onto the manifest,
    # taking advantage of dict mutability
    literal_character_manifest = {
        char: {
            'match': match,
            'open_count': 0,
        }
        for char, match in _literal_syntax_map.items()
    }

    literal_open_chars = {
        char: literal_character_manifest[char]
        for char, match in _literal_syntax_map.items()
    }

    literal_end_chars = {
        match['end_char']: literal_open_chars[char]
        for char, match in _literal_syntax_map.items()
        if match['end_char'] is not None
    }

    masking_end_char = None
    is_masking = False

    value_clone = value

    # First remove all escaped values
    for char, manifest_value in literal_character_manifest.items():
        match = manifest_value['match']
        end_char = match['end_char']
        escape_char = match['escape_char']

        if escape_char is not None:
            # Remove all escape open and end chars
            value_clone = value_clone.replace(
                escape_char + char,
                ''
            )

            if end_char is not None:
                value_clone = value_clone.replace(
                    escape_char + end_char,
                    ''
                )

    for index, char in enumerate(value_clone):
        # First check whether the current literal is masking,
        # only caring if the masking is finished
        if is_masking:
            if char == masking_end_char:
                is_masking = False
                masking_end_char = None

                literal_end_chars[char]['open_count'] -= 1

            continue

        # Check if the character is an open character
        if char in literal_open_chars:
            current_match = literal_open_chars[char]['match']

            # Check whether the open and close characters are the same
            if current_match['end_char'] == char:
                # If the open and close characters are the same,
                # a new masking literal has been started as already
                # open masking literals would be checked earlier
                is_masking = True
                masking_end_char = char

            literal_open_chars[char]['open_count'] += 1

            continue

        # Check if the character is an end character
        if char in literal_end_chars:
            # Check if the literal is open
            if literal_end_chars[char]['open_count'] > 0:
                literal_end_chars[char]['open_count'] -= 1

            else:
                # If no open literal is found, a syntax error has occurred
                raise exception.ExpressionSyntaxException(
                    f'Unexpected literal close character: {char} '
                    f'in {value} near index {index}'
                )

            continue

    # Finally, check if any literals are still open
    for char, manifest in literal_character_manifest.items():
        if manifest['open_count'] > 0:
            return True

    return False


def create_literal(char: str, match: LiteralMatch) -> BaseLiteral:
    """Creates a new literal value.

    Args:
        char (`str`): The character that started the literal.
        match (`LiteralMatch`): The match
            dictionary from character map.

    Returns:
        `BaseLiteral`: The new literal value.

    Raises:
        `ValueError`: If a value type that is not a type is passed.
        `UnknownLiteralType`: If the literal type is unknown.
    """

    # Use value type to determine which literal to create
    value_type = match.get('value_type')
    literal_class = match.get('literal_class')

    if isinstance(value_type, type):
        raise ValueError(f'Invalid value type for literal: {char}')

    if literal_class is None:
        raise exception.UnknownLiteralTypeException(
            f'Unknown literal type: {value_type}'
        )

    return literal_class(char, match)