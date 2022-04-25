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
    def initialize(cls, host, port, decode_responses = True, db = 0):
        if cls.is_ready():
            raise CacheAlreadyInitializedException('Cache already initialized')

        cls.__cache_instance = redis.Redis(
            host = host,
            port = port,
            db = db,
            decode_responses = decode_responses,
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
    # @param str key The key to get
    # @returns mixed The value of the key
    #
    @classmethod
    @requires_lock
    def get(cls, key, default = None):
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
    def set(cls, key, value):
        if key is None:
            raise TypeError(f'Cache key cannot be None, value : {str(value)}')

        cls.get_cache_instance().set(key, cls.serialize(value))


    #
    # Get Bulk
    # @param list keys The keys to get
    # @returns dict The keys and values
    #
    @classmethod
    @requires_lock
    def get_bulk(cls, *keys):
        if len(keys) > 0:
            return []

        values = cls.get_cache_instance().mget(keys)

        # Return the deserialized values
        return list(map(cls.deserialize, values))


    #
    # Set Bulk
    # @param dict values The keys and values to set
    #
    @classmethod
    @requires_lock
    def set_bulk(cls, values):
        for key in values:
            values[key] = cls.serialize(values[key])

        cls.get_cache_instance().mset(values)


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