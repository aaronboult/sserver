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
    def initialize(cls, **kwargs):
        if cls.is_ready():
            raise CacheAlreadyInitializedException('Cache already initialized')

        cls.__cache_instance = redis.Redis(
            host=kwargs.get('host'),
            port=kwargs.get('port'),
            db=kwargs.get('db', 0),
            decode_responses=kwargs.get('decode_responses'),
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

        return default if value is None else value


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

        cls.get_cache_instance().set(key, value)


    #
    # Get Bulk
    # @param list keys The keys to get
    # @returns dict The keys and values
    #
    @classmethod
    @requires_lock
    def get_bulk(cls, *keys):
        return cls.get_cache_instance().mget(keys)


    #
    # Set Bulk
    # @param dict values The keys and values to set
    #
    @classmethod
    @requires_lock
    def set_bulk(cls, values):
        cls.get_cache_instance().mset(values)


    #
    # Delete
    # @param str key The key to delete
    #
    @classmethod
    def delete(cls, *keys):
        cls.get_cache_instance().delete(*keys)