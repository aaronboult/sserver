from sserver.endpoint.BaseEndpoint import BaseEndpoint
from sserver.tool.ModuleTools import ModuleTools
from sserver.log.Logger import Logger


#
# Index Endpoint
#
class IndexEndpoint(BaseEndpoint):

    #
    # Get
    #
    def get(self):

        config = self.get_config()

        Logger.log('Config', config)

        return config.get('TEST_VAR')

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