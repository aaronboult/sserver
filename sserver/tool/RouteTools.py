from sserver.log.Logger import Logger
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.ModuleTools import ModuleTools
from sserver.tool.CacheTools import CacheTools

#
# Route Tools
#
class RouteTools:


    #
    # Clear
    #
    @staticmethod
    def clear():
        Logger.info('Clearing routes')
        route_manifest = CacheTools.pop('route_manifest', default = [])
        CacheTools.delete_bulk(route_manifest)




    #
    # Load
    #
    @staticmethod
    def load():

        RouteTools.clear()

        route_module_list = ModuleTools.load_from_filename('routes.py', fromlist=['routes'])

        route_manifest = []

        prefix_with_app_name = ConfigTools.fetch('PREFIX_ROUTE_WITH_APP_NAME')
        if prefix_with_app_name == None:
            prefix_with_app_name = False

        elif not isinstance(prefix_with_app_name, bool):
            raise TypeError(f'Config value for PREFIX_ROUTE_WITH_APP_NAME must be a boolean, got type {type(prefix_with_app_name)}')

        Logger.info('Loading Routes...')
        for module in route_module_list:
            route_list = ModuleTools.get_from_module(module, 'routes', [])

            for route in route_list:

                # Ensure routes are prefixed by a slash
                if route.url[0] != '/':
                    route.url = f'/{route.url}'
                
                # Ensure routes are not suffixed by a slash
                if route.url[-1] == '/':
                    route.url = route.url[:-1]

                if prefix_with_app_name:
                    # Get the apps folder name from the path and prepend to url
                    app_name = ModuleTools.get_app_path_from_path(module.__package__).split('.')[-1]
                    route.url = f'/{app_name}{route.url}'

                Logger.log('Found Route {}, handled by {}'.format(route.url, str(route.endpoint)))

                # Assign route and add to manifest
                CacheTools.serialize_set(route.url, route)

                route_manifest.append(route.url)

        CacheTools.serialize_set('route_manifest', route_manifest)