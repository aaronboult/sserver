class OptionMixin:

    def __init__(self, **kwargs):
        self._options = {}
        
        if kwargs.get('options') is not None:
            self.setOptions(kwargs.get('options'))

    def setOptions(self, options):
        self._options = options
    
    def getOptions(self):
        return self._options
    
    def setOption(self, key, value):
        self._options[key] = value
    
    def setDefaultValue(self, key, value):
        if key not in self._options:
            pass

    def getOption(self, key):
        return self._options.get(key)