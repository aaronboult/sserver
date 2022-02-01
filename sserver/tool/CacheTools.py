import uwsgi

class CacheTools:
    
    
    #
    # Get
    # @param str key The key to get
    # @return mixed The value of the key
    #
    @staticmethod
    def get(key):
        return uwsgi.cache_get(key)
    

    #
    # Set
    # @param str key The key to set
    # @param bytes value The value to set
    #
    @staticmethod
    def set(key, value):
        uwsgi.cache_update(key, value)
    

    #
    # Deserialize Get
    # @param str key The key to get
    # @return mixed The deserialized object
    #
    @staticmethod
    def deserialize_get(key):
        from pickle import loads
        
        return loads(CacheTools.get(key))


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
    # @return dict The keys and values
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
    # @return dict The keys and deserialized values
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