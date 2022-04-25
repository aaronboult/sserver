from sserver.log.Logger import Logger
from sserver.mixin.OptionMixin import OptionMixin
from sserver.tool.CacheTools import CacheTools
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.RouteTools import RouteTools


#
# Server
# @note This is never instantiated
#
class Server(OptionMixin):


    #
    # Handle Request
    #
    def handle_request(self):

        status, headers, content = None, None, None

        try:
        
            response = self.get_response()

            # Default headers and status to an OK HTML response
            headers = response.get('headers', [('Content-Type', 'text/html')])

            # Get status and ensure it is bytes
            status = response.get('status', '200 OK')

            # Get content and ensure it is bytes
            content = response.get('body', '')
            if not isinstance(content, bytes):
                content = str(content).encode('utf-8')

        except Exception as e:
            Logger.exception(e, reraise = False)

            # @note Ensure a response for unexplained errors
            headers = [('Content-Type', 'text/html')]
            status = '500 Internal Server Error'
            content = b'500 Internal Server Error'

        start_response = self.getOption('start_response')
        start_response(status, headers)

        return [content]


    #
    # Get Response
    #
    def get_response(self):

        # @note Wrap entire request handle in try/except to report 500 errors
        try:

            route = self.get_route()

            if route == None:
                return self.handle_404()

            else:
                return self.handle_route(route)

        except Exception as e:

            Logger.exception(e)

            return self.handle_500()


    #
    # Get Route
    #
    def get_route(self):

        environment = self.getOption('environment')

        uri = environment.get('REQUEST_URI')

        route = CacheTools.get(uri)

        return route


    #
    # Handle 404
    #
    def handle_404(self):
        return {
            'body' : '404 Not Found',
        }
    

    #
    # Handle 405
    #
    def handle_405(self):
        return {
            'body' : '405 Method Not Allowed',
        }
    

    #
    # Handle 500
    #
    def handle_500(self):
        return {
            'body' : '500 Internal Server Error',
        }


    #
    # Handle Route
    #
    def handle_route(self, route):

        environment = self.getOption('environment')
        method = environment.get('REQUEST_METHOD')
        content = None

        if method == 'GET':
            content = route.endpoint().get()

        elif method == 'POST':
            content = route.endpoint().post()

        elif method == 'PUT':
            content = route.endpoint().put()

        elif method == 'PATCH':
            content = route.endpoint().patch()

        elif method == 'DELETE':
            content = route.endpoint().delete()

        else:
            return self.handle_405()

        return {
            'body' : content,
        }


#
# Application
#
def application(environment, start_response):
    server = Server()

    server.setOptions({
        'environment'    : environment,
        'start_response' : start_response
    })

    return server.handle_request()


#
# Initialize Server
#
def initialize(**kwargs):
    ConfigTools.load(**kwargs.get('config', {}))
    RouteTools.load()