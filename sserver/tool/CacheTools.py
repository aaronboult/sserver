from sserver.log.Logger import Logger
import uwsgi


#
# Cache Tools
#
class CacheTools:


    #
    # Clear Cache
    #
    @staticmethod
    def clear():
        Logger.log('Clearing cache')
        uwsgi.cache_clear()
    

    #
    # Pop
    # @param str key The key to pop
    # @returns mixed The value of the key
    #
    @staticmethod
    def pop(key, default = None):
        value = CacheTools.get(key, default = default)
        CacheTools.delete(key)
        return value


    #
    # Get
    # @param str key The key to get
    # @returns mixed The value of the key
    #
    @staticmethod
    def get(key, default = None):
        if key is None:
            raise TypeError('Cache key cannot be None')

        value = uwsgi.cache_get(key)

        return default if value is None else value


    #
    # Set
    # @param str key The key to set
    # @param bytes value The value to set
    #
    @staticmethod
    def set(key, value):
        if key is None:
            raise TypeError(f'Cache key cannot be None, value : {str(value)}')

        uwsgi.cache_update(key, value)
    

    #
    # Deserialize Get
    # @param str key The key to get
    # @returns mixed The deserialized object
    #
    @staticmethod
    def deserialize_get(key):
        from pickle import loads

        serialized_value = CacheTools.get(key)

        if serialized_value is not None:
            return loads(serialized_value)

        return None


    #
    # Serialize Set
    # @param str key The key to set
    # @param mixed value The value to serialize and set
    #
    @staticmethod
    def serialize_set(key, value):
        from pickle import dumps

        CacheTools.set(key, dumps(value))
    

    #
    # Get Bulk
    # @param list keys The keys to get
    # @returns dict The keys and values
    #
    @staticmethod
    def get_bulk(keys):
        values = {}

        for key in keys:
            values[key] = CacheTools.get(key)
    
        return values
    

    #
    # Set Bulk
    # @param dict values The keys and values to set
    #
    @staticmethod
    def set_bulk(values):
        for key, value in values.items():
            CacheTools.set(key, value)


    #
    # Deserialize Get Bulk
    # @param list keys The keys to get
    # @returns dict The keys and deserialized values
    #
    @staticmethod
    def deserialize_get_bulk(keys):
        from pickle import loads

        values = CacheTools.get_bulk(keys)

        for key, value in values.items():
            values[key] = loads(value)
        
        return values
    

    #
    # Serialize Set Bulk
    # @param dict values The keys and values to serialize and set
    #
    @staticmethod
    def serialize_set_bulk(values):
        from pickle import dumps

        for key, value in values.items():
            CacheTools.set(key, dumps(value))
    

    #
    # Delete
    # @param str key The key to delete
    #
    @staticmethod
    def delete(key):
        if key is None:
            raise TypeError('Cache key cannot be None')

        uwsgi.cache_del(key)
    

    #
    # Delete Bulk
    # @param list keys The keys to delete
    #
    @staticmethod
    def delete_bulk(keys):
        for key in keys:
            CacheTools.delete(key)