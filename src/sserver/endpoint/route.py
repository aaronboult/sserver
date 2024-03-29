"""Handles URL routing."""

from typing import Any
from sserver.endpoint.base_endpoint import BaseEndpoint
from sserver.util import log, config, cache, module


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

    Raises:
        TypeError: If the `prefix_with_app_name` config value is not a
            bool.
    """

    clear()

    ROUTE_FILENAME = config.get('route_filename')
    ROUTE_LIST_VARIABLE = config.get('route_list_variable')

    route_module_list = module.load_from_filename(f'{ROUTE_FILENAME}.py')

    route_manifest = []

    log.info('Loading Routes...', route_module_list)
    for route_module in route_module_list:

        # Get the current app name
        APP_NAME = module.get_app_name(route_module.__name__)
        prefix_route_with_app_name = config.get(
            'prefix_route_with_app_name',
            app_name=APP_NAME
        )

        if prefix_route_with_app_name is None:
            prefix_route_with_app_name = False

        elif not isinstance(prefix_route_with_app_name, bool):
            error_message = (
                'Config value for prefix_route_with_app_name must be a ',
                f'boolean, got type {type(prefix_route_with_app_name)}',
            )

            raise TypeError(''.join(error_message))

        route_list = module.get_from_module(
            route_module,
            ROUTE_LIST_VARIABLE,
            [],
        )
        for route in route_list:

            # Ensure routes are prefixed by a slash
            if route.url[0] != '/':
                route.url = f'/{route.url}'

            # If prefix with app name is True, prefix the route url
            if prefix_route_with_app_name:
                route.url = f'/{APP_NAME}{route.url}'

            info_message = (
                f'Found Route "{route.url}", handled by ',
                f'{str(route.endpoint)}',
            )

            log.info(''.join(info_message))

            # Assign route and add to manifest
            cache.set(route.url, route)

            route_manifest.append(route.url)

    cache.set('route_manifest', route_manifest)
