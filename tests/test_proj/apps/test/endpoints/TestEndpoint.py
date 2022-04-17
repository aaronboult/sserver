from sserver.endpoint.BaseEndpoint import BaseEndpoint
from sserver.log.Logger import Logger


#
# Test Endpoint
#
class TestEndpoint(BaseEndpoint):


    #
    # Template
    #
    template = 'test.html'


    #
    # Get
    #
    def get(self):

        config = self.get_config()

        return super().get(**{
            'TEST_VAR' : self.get_from_config('TEST_VAR'),
        })

    #
    # Post
    #
    def post(self):
        return 'post'

    #
    # Put
    #
    def put(self):
        return 'put'

    #
    # Patch
    #
    def patch(self):
        return 'patch'

    #
    # Delete
    #
    def delete(self):
        return 'delete'