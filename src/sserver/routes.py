from typing import Any

from sserver.endpoint.BaseEndpoint import BaseEndpoint


class Route:
    """Wrapping class for a URL route."""


    def __init__(self, url: str, name: str, endpoint: BaseEndpoint):
        """Create a route instance with the given
        `url`, `name`, and `endpoint`.

        Args:
            url (`str`): The url of the route.
            name (`str`): The name of the route.
            endpoint (`BaseEndpoint`): The endpoing
                class to handle responses.
        """

        self.url = url
        self.name = name
        self.endpoint = endpoint


    def __str__(self):
        return f'<{self.__class__.__name__} url="{self.url}">'


def route(url: str, name: str, endpoint: BaseEndpoint) -> Route:
    """Generates a route class instance needed for
    routing.

    Args:
        url (`str`): The url of the route.
        name (`str`): The name of the route.
        endpoint (`BaseEndpoint`): The endpoing
            class to handle responses.

    Returns:
        `Route`: The route class instance.
    """

    return Route(url, name, endpoint)