from sserver.log.Logger import Logger
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
        Logger.log('Clearing routes')
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

        Logger.log('Loading Routes...')
        for module in route_module_list:
            route_list = ModuleTools.get_from_module(module, 'routes', [])

            for route in route_list:
                Logger.log('Found Route {}, handled by {}'.format(route.url, str(route.endpoint)))

                # Assign route and add to manifest
                CacheTools.serialize_set(route.url, route)

                route_manifest.append(route.url)

        CacheTools.serialize_set('route_manifest', route_manifest)