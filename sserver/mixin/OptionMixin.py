class OptionMixin:


    def __init__(self, **kwargs):
        self._options = {}
        
        if kwargs.get('options') is not None:
            self.setOptions(kwargs.get('options'))


    #
    # Set Options
    # @param dict options The options to set
    #
    def setOptions(self, options):
        self._options = options


    #
    # Get Options
    # @returns dict The options
    #
    def getOptions(self):
        return self._options


    #
    # Get Option
    # @param str key The key of the option to get
    # @param mixed default The value to assign
    #
    def setOption(self, key, value):
        self._options[key] = value


    #
    # Set Default Option
    # @param str key The key of the option to default
    # @param mixed default The default value to assign
    #
    def setDefaultOption(self, key, value):
        if key not in self._options:
            self._options[key] = value


    #
    # Get Option
    # @param str key The key of the option to get
    # @returns mixed The value of the option
    #
    def getOption(self, key):
        return self._options.get(key)