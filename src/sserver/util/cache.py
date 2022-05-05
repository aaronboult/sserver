"""Provides an interface to communicate with the Redis cache."""

import pickle
from typing import Any, Callable, Dict, List, Union
from sserver.util import log
from sserver.util.exception import (
    CacheNotInitializedException,
    CacheAlreadyInitializedException
)
from redis import Redis
from functools import wraps


class Cache:
    """A wrapper class for the cache."""


    __cache_instance: Redis = None


    @classmethod
    def get_cache_instance(cls) -> Redis:
        """Get the current cache instance.

        Raises:
            CacheNotInitializedException: If the cache is not initialized.

        Returns:
            `Redis`: The cache instance.
        """

        if not cls.is_ready():
            raise CacheNotInitializedException('Cache must be initialized before use')

        return cls.__cache_instance


    @classmethod
    def set_cache_instance(cls, cache_instance: Redis):
        """Set the cache instance if not already set.

        Args:
            cache_instance (`Redis`): The cache instance to assign.

        Raises:
            CacheAlreadyInitializedException: If the cache is already set.
        """

        if cls.is_ready():
            raise CacheAlreadyInitializedException('The cache instance is already set')

        cls.__cache_instance = cache_instance


    @classmethod
    def is_ready(cls) -> bool:
        """Checks if the cache is ready for use.

        Returns:
            `bool`: True if the cache is ready for use, otherwise False.
        """

        return cls.__cache_instance is not None


def requires_lock(func: Callable) -> Callable:
    """Requires lock decorate; ensures the cache is locked when function
    is executing.

    Args:
        func (`Callable`): The decorated function.

    Returns:
        `Callable`: The wrapped function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        return func(*args, **kwargs)
        # try:
        #     with r.lock('my-lock-key', blocking_timeout=5) as lock:
        #         # code you want executed only after the lock has been acquired
        #         pass
        # except redis.LockError:
        #     # the lock wasn't acquired
        #     pass

    return wrapper


def initialize(host: str, port: int, decode_strings: bool = True, db: int = 0):
    """Initialize the cache.

    Args:
        host (`str`): The cache hostname.
        port (`int`): The cache port.
        decode_strings (`bool`, optional): Whether or not to decode
            strings by default. Defaults to True.
        db (`int`, optional): The database number. Defaults to 0.

    Raises:
        CacheAlreadyInitializedException: If the cache is already initialized.
    """

    if Cache.is_ready():
        raise CacheAlreadyInitializedException('Cache already initialized')

    cache_instance = Redis(
        host = host,
        port = port,
        db = db,
        # This causes errors
        # decode_responses = decode_strings,
    )

    Cache.set_cache_instance(cache_instance)


@requires_lock
def clear():
    """Clear the cache."""

    log.info('Clearing cache')
    Cache.get_cache_instance().flushdb()


def pop(key: str, default: Any = None) -> Any:
    """Get a value from the cache and remove the cache entry.

    Args:
        key (`str`): The key to get the value from.
        default (`Any`, optional): The value to return if the key is not
            found. Defaults to None.

    Returns:
        `Any`: The value from the cache, or `default` if not found.
    """

    value = get(key, default = default)

    delete(key)

    return value


@requires_lock
def get(*key_list: str, default: Union[Any, List[Any]] = None) -> Union[Any, List[Any]]:
    """Get values from the cache.

    Args:
        *key_list (`str`): The list of keys to get.
        default (`Any` | `List[Any]`, optional): The default value or list of values.
            Defaults to None.

    Returns:
        `Any` | `List[Any]`: The values from the cache, or single value
            if only one key, or the associated default value if not found.
    """

    # If only one key supplies, wrap default to work with zip
    if len(key_list) == 1 or not isinstance(default, list):
        default = (default,)

    if isinstance(default, list):
        KEY_LIST_LENGTH = len(key_list)
        DEFAULT_LENGTH = len(default)

        # Ensure default list is at least as long as key list
        if KEY_LIST_LENGTH > DEFAULT_LENGTH:
            default.extend(None for _ in range(KEY_LIST_LENGTH - DEFAULT_LENGTH))

    # Convert each key into a tuple to allow passing with *
    key_list = list(zip(key_list, default))

    # Generate a list of values using the key list
    # Passes either just a key or key, default
    value = [_get(*key_tuple) for key_tuple in key_list]

    if len(value) == 1:
        return value[0]

    return value


def _get(key: str, default: Any = None) -> Any:
    """Get the value at `key` from the cache.

    Args:
        key (`str`): The key to get the value from.
        default (`Any`, optional): The default value if `key` is not
            found. Defaults to None.

    Raises:
        TypeError: If the key is not a string.

    Returns:
        `Any`: The value from the cache or `default` if not found.
    """

    if not isinstance(key, str):
        raise TypeError('Cache key must be of type str')

    value = Cache.get_cache_instance().get(key)

    return default if value is None else deserialize(value)


@requires_lock
def set(key: str = None, value: Any = None, key_value: Dict[str, Any] = None):
    """Set the key `key` to value `value` in the cache, or store the same
    key-value mappings in `key_value` in the cache.

    Args:
        key (`str`, optional): The key to store in. Defaults to None.
        value (`Any`, optional): The value to store in. Defaults to None.
        key_value (`Dict[str, Any]`, optional): The key value mappings
            to store. Defaults to None.

    Raises:
        TypeError: If the key is not a string when `key_value` is not passed.
    """

    if isinstance(key_value, dict):
        for key, value in key_value.items():
            set(key, value)
        return

    elif not isinstance(key, str):
        raise TypeError(f'Cache key must be of type str, value : {str(value)}')

    Cache.get_cache_instance().set(key, serialize(value))


def serialize(value: Any) -> bytes:
    """Serialize `value` into an array of bytes.

    Args:
        value (`Any`): The value to serialize.

    Returns:
        `bytes`: The serialized value.
    """

    return pickle.dumps(value)


def deserialize(byte_stream: bytes) -> Any:
    """Deserialize `byte_stream` into its original form.

    Args:
        byte_stream (`bytes`): The bytes to deserialize.

    Returns:
        `Any`: The original form of `byte_stream`.
    """

    return pickle.loads(byte_stream)


def delete(*keys: str):
    """Delete `keys` from the cache.

    Args:
        *keys (`str`): The keys to remove from the cache.
    """

    if len(keys) > 0:
        Cache.get_cache_instance().delete(*keys)