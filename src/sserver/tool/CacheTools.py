import pickle
from sserver.log.Logger import Logger
from sserver.tool.exception import (
    CacheNotInitializedException,
    CacheAlreadyInitializedException
)
import redis
from functools import wraps


#
# Cache Tools
#
class CacheTools:


    #
    # Cache Instance
    #
    __cache_instance = None


    #
    # Requires Lock Decorator
    #
    def requires_lock(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
        # try:
        #     with r.lock('my-lock-key', blocking_timeout=5) as lock:
        #         # code you want executed only after the lock has been acquired
        #         pass
        # except redis.LockError:
        #     # the lock wasn't acquired
        #     pass


    #
    # Initialize
    #
    @classmethod
    def initialize(cls, host, port, decode_strings = True, db = 0):
        if cls.is_ready():
            raise CacheAlreadyInitializedException('Cache already initialized')

        cls.__cache_instance = redis.Redis(
            host = host,
            port = port,
            db = db,
            # @todo This causes errors
            # decode_responses = decode_strings,
        )


    #
    # Get Cache Instance
    #
    @classmethod
    def get_cache_instance(cls):
        if not cls.is_ready():
            raise CacheNotInitializedException('Cache must be initialized before use')

        return cls.__cache_instance


    #
    # Is Ready
    #
    @classmethod
    def is_ready(cls):
        return cls.__cache_instance is not None


    #
    # Clear Cache
    #
    @classmethod
    @requires_lock
    def clear(cls):
        Logger.info('Clearing cache')
        cls.get_cache_instance().flushdb()


    #
    # Pop
    # @param str key The key to pop
    # @returns mixed The value of the key
    #
    @classmethod
    def pop(cls, key, default = None):
        value = cls.get(key, default = default)
        cls.delete(key)
        return value


    #
    # Get
    # @param str|list key The key(s) to get
    # @param mixed default The default value
    # @returns mixed The value of the key
    #
    @classmethod
    @requires_lock
    def get(cls, *key_list, default = None):
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
        value = [cls._get(*key_tuple) for key_tuple in key_list]

        if len(value) == 1:
            return value[0]

        return value


    #
    # Get
    # @param str key The key to get
    # @param mixed default The default value
    # @returns mixed The value of the key
    #
    @classmethod
    def _get(cls, key, default = None):
        if key is None:
            raise TypeError('Cache key cannot be None')

        value = cls.get_cache_instance().get(key)

        return default if value is None else cls.deserialize(value)


    #
    # Set
    # @param str key The key to set
    # @param bytes value The value to set
    #
    @classmethod
    @requires_lock
    def set(cls, key = None, value = None, key_value = None):
        if isinstance(key_value, dict):
            for key, value in key_value.items():
                cls.set(key, value)
            return

        elif not isinstance(key, str):
            raise TypeError(f'Cache key must be of type str, value : {str(value)}')

        cls.get_cache_instance().set(key, cls.serialize(value))


    #
    # Serialize
    # @param mixed value The value to serialize
    #
    @staticmethod
    def serialize(value):
        return pickle.dumps(value)


    #
    # Deserialize
    # @param bytes value The value to deserialize
    #
    @staticmethod
    def deserialize(value):
        return pickle.loads(value)


    #
    # Delete
    # @param str key The key to delete
    #
    @classmethod
    def delete(cls, *keys):
        if len(keys) > 0:
            cls.get_cache_instance().delete(*keys)