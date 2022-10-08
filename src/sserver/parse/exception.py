"""Parsing exceptions."""


class UnknownLiteralTypeException(Exception):
    """Raised when an unknown literal type is encountered."""


class UnknownOperatorException(Exception):
    """Raised when an unknown operator is encountered."""


class ExpressionSyntaxException(Exception):
    """Raised when invalid expression syntax is encountered."""


class LiteralEndCharacterNotDefinedException(Exception):
    """Raised when the end character for a literal is not defined."""


class LiteralCharacterAlreadyInUseException(Exception):
    """Raised when a literal character is already in use."""


class MissingOperatorFunctionException(Exception):
    """Raised when an operator function is missing."""


class MissingOperatorPrecedenceException(Exception):
    """Raised when an operator precedence is missing."""
