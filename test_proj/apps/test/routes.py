from sserver.routes import route
from test_proj.apps.test.endpoints.IndexEndpoint import IndexEndpoint

routes = [
    route('/', 'index', IndexEndpoint),
    route('/test', 'test', 'test'),
]