"""Handles URL routing."""

from typing import Any
from sserver.endpoint.base_endpoint import BaseEndpoint
from sserver.util import log
from sserver.util import config
from sserver.util import module
from sserver.util import cache


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


def check_route_valid(route: Any) -> bool:
    if isinstance(route, Route):
        return True

    if (hasattr(route, 'url') and hasattr(route, 'name') and
            hasattr(route, 'endpoint')):
        return True

    if hasattr(route, '__get__'):
        if hasattr(route.__get__, '__call__'):
            # check get for url, name and endpoint
            return False

    return False


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


def clear():
    """Clear the loaded routes."""

    log.info('Clearing routes')
    route_manifest = cache.pop('route_manifest', default=[])
    cache.delete(*route_manifest)


def load():
    """Load routes from each `routes.py` file in the project.

    Future:
        `route.py` will be moved into the project config.

    Raises:
        TypeError: If the `prefix_with_app_name` config value is not a
            bool.
    """

    clear()

    route_module_list = module.load_from_filename('route.py')

    route_manifest = []

    prefix_with_app_name = config.get('prefix_route_with_app_name')
    if prefix_with_app_name is None:
        prefix_with_app_name = False

    elif not isinstance(prefix_with_app_name, bool):
        error_message = (
            'Config value for prefix_route_with_app_name must be a boolean,',
            f'got type {type(prefix_with_app_name)}',
        )

        raise TypeError(''.join(error_message))

    log.info('Loading Routes...', route_module_list)
    for route_module in route_module_list:
        route_list = module.get_from_module(route_module, 'routes', [])
        for route in route_list:

            # Ensure routes are prefixed by a slash
            if route.url[0] != '/':
                route.url = f'/{route.url}'

            if prefix_with_app_name:
                # Get the apps folder name from the path and prepend to url
                app_name = module.get_app_name(route_module.__name__)
                route.url = f'/{app_name}{route.url}'

            info_message = (
                f'Found Route "{route.url}", handled by ',
                f'{str(route.endpoint)}',
            )

            log.info(''.join(info_message))

            # Assign route and add to manifest
            cache.set(route.url, route)

            route_manifest.append(route.url)

    cache.set('route_manifest', route_manifest)
