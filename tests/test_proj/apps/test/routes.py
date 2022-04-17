from sserver.routes import route
from test_proj.apps.test.endpoints.IndexEndpoint import IndexEndpoint
from test_proj.apps.test.endpoints.TestEndpoint import TestEndpoint

routes = [
    route('/', 'index', IndexEndpoint),
    route('/test', 'test', TestEndpoint),
]