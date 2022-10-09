class TooManyTagArgumentsException(Exception):
    """Raised when a template tag is called with too many arguments."""


class MissingTagArgumentsException(Exception):
    """Raised when a template tag is called with too few arguments."""


class UnknownTagException(Exception):
    """Raised when a template tag is called with an unknown tag name."""


class UnclosedBlockTagException(Exception):
    """Raised when a block tag is not closed."""


class UnknownTagConditionalExpressionException(Exception):
    """Raised when a conditional expression is not recognized."""


class MissingTagFunctionException(Exception):
    """Raised when a tag function is not found."""


class TagAlreadyRegisteredException(Exception):
    """Raised when a tag is already registered."""


class TemplateArgumentException(Exception):
    """Raised when a template argument is invalid."""
