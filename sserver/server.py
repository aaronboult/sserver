from os import environ
from sserver.log.Logger import Logger
from sserver.mixin.OptionMixin import OptionMixin


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
            # if not isinstance(status, bytes):
            #     status = status.encode('utf-8')

            # Get content and ensure it is bytes
            content = response.get('body', '')
            if not isinstance(content, bytes):
                content = content.encode('utf-8')
        
        except:
            # @note Ensure a response for unexplained errors
            headers = [('Content-Type', 'text/html')]
            status = '500 Internal Server Error'
            content = '500 Internal Server Error'

        # @note If this raises an error there is a serious problem; start_response is passed by uwsgi
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

        except:
            return self.handle_500()


    #
    # Get Route
    #
    def get_route(self):

        Logger.log(self.getOption('enviroment'))

        return None


    #
    # Handle 404
    #
    def handle_404(self):
        return {
            'body' : '404 Not Found',
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
        return {
            'body' : 'Routing',
        }


def application(environment, start_response):
    server = Server()

    server.setOptions({
        'environment'    : environment,
        'start_response' : start_response
    })

    return server.handle_request()