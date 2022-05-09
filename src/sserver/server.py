from typing import Callable, Dict, List, Union
from sserver.mixin.option_mixin import OptionMixin
from sserver.endpoint import route
from sserver.util import log
from sserver.util import cache
from sserver.util import config


class BaseServer(OptionMixin):

    def __init__(self, environment: Dict[str, str] = None,
                 start_response: Callable = None):
        """Initialize the server.

        Args:
            environment (`Dict[str, str]`): The environment dict.
            start_response (`Callable`): The start_response function.
        """

        if environment is not None and start_response is not None:
            super().__init__({
                'environment': environment,
                'start_response': start_response,
            })

    def __iter__(self):
        """Get a response from the server.

        Yields:
            `str`: The server response.
        """

        yield self.handle_request()

    def handle_request(self) -> bytes:
        """Handle a WSGI request.

        Returns:
            `bytes`: The response content.
        """

        status, headers, content = None, None, None

        try:

            response = self.get_response()

            # Default headers and status to an OK HTML response
            headers = response.get('headers',
                                   [('Content-Type', 'text/html')])

            # Get status and ensure it is bytes
            status = response.get('status', '200 OK')

            # Get content and ensure it is bytes
            content = response.get('body', '')
            if not isinstance(content, bytes):
                content = str(content).encode('utf-8')

        except Exception as e:
            log.exception(e, reraise=False)

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

            matched_route = self.get_route()

            if matched_route is None:
                return self.handle_404()

            else:
                return self.handle_route(matched_route)

        except Exception as e:

            log.exception(e)

            return self.handle_500()

    def get_route(self) -> Union[route.Route, None]:
        """Get the matching route, if any, using the REQUEST_URI.

        Returns:
            `Route` | `None`: The matching route or None if not found.
        """

        environment = self.getOption('environment')

        uri = environment.get('REQUEST_URI')

        matched_route = cache.get(uri)

        return matched_route

    def handle_route(self, matched_route: route.Route) -> Dict[str, str]:
        """Handle the request using the matched `matched_route`.

        Args:
            matched_route (`Route`): The matched route.

        Returns:
            `Dict[str, str]`: The routes response.
        """

        environment = self.getOption('environment')
        method = environment.get('REQUEST_METHOD')
        content = None

        endpoint = matched_route.endpoint()

        method_map = {
            'GET': endpoint.get,
            'POST': endpoint.post,
            'PUT': endpoint.put,
            'DELETE': endpoint.delete,
        }

        if method in method_map:
            content = method_map[method]()

        else:
            return self.handle_405()

        return {
            'body': content,
        }

    def handle_404(self) -> Dict[str, str]:
        """Handle 404 not found.

        Returns:
            `Dict[str, str]`: The 404 response.
        """

        return {
            'body': '404 Not Found',
        }

    def handle_405(self) -> Dict[str, str]:
        """Handle 405 method not allowed.

        Returns:
            `Dict[str, str]`: The 405 response.
        """

        return {
            'body': '405 Method Not Allowed',
        }

    def handle_500(self) -> Dict[str, str]:
        """Handle 500 internal server errors.

        Returns:
            `Dict[str, str]`: The 500 response.
        """

        return {
            'body': '500 Internal Server Error',
        }


def application(environment, start_response) -> List[bytes]:

    server = BaseServer()

    server.setOptions({
        'environment': environment,
        'start_response': start_response
    })



    return [server.handle_request()]


config.load()
route.load()
