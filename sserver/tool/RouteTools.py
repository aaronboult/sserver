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
        # @todo Implement route clearing


    #
    # Load
    #
    @staticmethod
    def load():

        RouteTools.clear()

        route_module_list = ModuleTools.load_from_filename('routes.py', fromlist=['routes'])

        Logger.log('Loading Routes...')
        for module in route_module_list:
            route_list = ModuleTools.get_from_module(module, 'routes', [])

            for route in route_list:
                Logger.log('Found Route {}, handled by {}'.format(route.url, str(route.endpoint)))
                CacheTools.serialize_set(route.url, route)