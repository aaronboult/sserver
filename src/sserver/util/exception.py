class CacheNotInitializedException(Exception):
    """Raised when the operations are attempted on the cache but it has not
    yet been initialized.
    """


class CacheAlreadyInitializedException(Exception):
    """Raised when initialization is attempted on the cache, but it has
    already been initialized.
    """


class MissingConfigValueException(Exception):
    """Raised when an invalid config value is set."""