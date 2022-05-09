from typing import Any, Dict


class OptionMixin:
    """A mixin giving classes assigned options."""

    def __init__(self, options: Dict[Any, Any] = None):
        """Pass options in the class constructor.

        Args:
            options (`Dict[Any, Any]`, optional): The class
            options. Defaults to None.
        """

        self._options = {}

        if options is not None:
            self.setOptions(options)

    def setOptions(self, options: Dict[Any, Any]):
        """Set the class options.

        Args:
            options (`Dict[Any, Any]`): The class options.
        """

        self._options = options

    def getOptions(self) -> Dict[Any, Any]:
        """Get the class options.

        Returns:
            `Dict[Any, Any]`: The class options.
        """

        return self._options

    def setOption(self, key: str, value: Any):
        """Set the option with key `key` to `value`.

        Args:
            key (`str`): The option key.
            value (`Any`): The option value.
        """

        self._options[key] = value

    def getOption(self, key: str, default: Any = None) -> Any:
        """Get the value of option `key`, if not found
        return `default`.

        Args:
            key (`str`): The option key.
            default (`Any`, optional): The value to return
                if `key` is not set. Defaults to None.

        Returns:
            `Any`: The value of the option.
        """

        if key in self._options:
            return self._options.get(key)

        return default
