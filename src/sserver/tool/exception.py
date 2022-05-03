class CacheNotInitializedException(Exception):
    """Raised when the operations are attempted on the cache but it has not
    yet been initialized.
    """

    pass


class CacheAlreadyInitializedException(Exception):
    """Raised when initialization is attempted on the cache, but it has
    already been initialized.
    """

    pass