from sserver.endpoint.BaseEndpoint import BaseEndpoint


#
# Index Endpoint
#
class IndexEndpoint(BaseEndpoint):

    #
    # Get
    #
    def get(self):
        return 'get'

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