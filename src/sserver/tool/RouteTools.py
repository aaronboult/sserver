from sserver.log.Logger import Logger
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.ModuleTools import ModuleTools
from sserver.tool.CacheTools import CacheTools

#
# Route Tools
#
class RouteTools:
    """Handles URL routing."""


    @staticmethod
    def clear():
        """Clear the loaded routes."""

        Logger.info('Clearing routes')
        route_manifest = CacheTools.pop('route_manifest', default = [])
        CacheTools.delete(*route_manifest)


    @staticmethod
    def load():
        """Load routes from each `routes.py` file in the project.

        Future:
            `routes.py` will be moved into the project config.

        Raises:
            TypeError: If the `prefix_with_app_name` config value is not a
                bool.
        """

        RouteTools.clear()

        route_module_list = ModuleTools.load_from_filename('routes.py')

        route_manifest = []

        prefix_with_app_name = ConfigTools.fetch('prefix_route_with_app_name')
        if prefix_with_app_name == None:
            prefix_with_app_name = False

        elif not isinstance(prefix_with_app_name, bool):
            raise TypeError(f'Config value for prefix_route_with_app_name must be a boolean, got type {type(prefix_with_app_name)}')

        Logger.info('Loading Routes...')
        for module in route_module_list:
            route_list = ModuleTools.get_from_module(module, 'routes', [])

            for route in route_list:

                # Ensure routes are prefixed by a slash
                if route.url[0] != '/':
                    route.url = f'/{route.url}'

                if prefix_with_app_name:
                    # Get the apps folder name from the path and prepend to url
                    app_name = ModuleTools.get_app_name(module.__name__)
                    route.url = f'/{app_name}{route.url}'

                Logger.log('Found Route {}, handled by {}'.format(route.url, str(route.endpoint)))

                # Assign route and add to manifest
                CacheTools.set(route.url, route)

                route_manifest.append(route.url)

        CacheTools.set('route_manifest', route_manifest)