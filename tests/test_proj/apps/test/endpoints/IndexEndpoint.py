from sserver.endpoint.BaseEndpoint import BaseEndpoint
from sserver.log.Logger import Logger


#
# Index Endpoint
#
class IndexEndpoint(BaseEndpoint):

    #
    # Get
    #
    def get(self):
        return 'Get index'

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