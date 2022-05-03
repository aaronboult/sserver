from typing import Dict, List, Union
from sserver.log.Logger import Logger
from sserver.mixin.OptionMixin import OptionMixin
from sserver.routes import Route
from sserver.tool.CacheTools import CacheTools
from sserver.tool.ConfigTools import ConfigTools
from sserver.tool.RouteTools import RouteTools


class BaseServer(OptionMixin):


    def handle_request(self) -> bytes:
        """Handle a WSGI request.

        Returns:
            `bytes`: The response content.
        """

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

            # Ensure a response for unexplained errors
            headers = [('Content-Type', 'text/html')]
            status = '500 Internal Server Error'
            content = b'500 Internal Server Error'

        start_response = self.getOption('start_response')
        start_response(status, headers)

        return content


    def get_response(self) -> Dict[str, str]:
        """Get the requests response.

        Returns:
            `Dict[str, str]`: The response dict.
        """

        # Wrap entire request handle in try/except to report 500 errors
        try:

            route = self.get_route()

            if route == None:
                return self.handle_404()

            else:
                return self.handle_route(route)

        except Exception as e:

            Logger.exception(e)

            return self.handle_500()


    def get_route(self) -> Union[Route, None]:
        """Get the matching route, if any, using the REQUEST_URI.

        Returns:
            `Route` | `None`: The matching route or None if not found.
        """

        environment = self.getOption('environment')

        uri = environment.get('REQUEST_URI')

        route = CacheTools.get(uri)

        return route


    def handle_route(self, route: Route) -> Dict[str, str]:
        """Handle the request using the matched `route`.

        Args:
            route (`Route`): The matched route.

        Returns:
            `Dict[str, str]`: The routes response.
        """

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


    def handle_404(self) -> Dict[str, str]:
        """Handle 404 not found.

        Returns:
            `Dict[str, str]`: The 404 response.
        """

        return {
            'body' : '404 Not Found',
        }
    

    def handle_405(self) -> Dict[str, str]:
        """Handle 405 method not allowed.

        Returns:
            `Dict[str, str]`: The 405 response.
        """

        return {
            'body' : '405 Method Not Allowed',
        }
    

    def handle_500(self) -> Dict[str, str]:
        """Handle 500 internal server errors.

        Returns:
            `Dict[str, str]`: The 500 response.
        """

        return {
            'body' : '500 Internal Server Error',
        }


def application(environment, start_response) -> List[bytes]:

    server = BaseServer()

    server.setOptions({
        'environment'    : environment,
        'start_response' : start_response
    })

    return [server.handle_request()]


def initialize(**kwargs):
    ConfigTools.load(**kwargs.get('config', {}))
    RouteTools.load()