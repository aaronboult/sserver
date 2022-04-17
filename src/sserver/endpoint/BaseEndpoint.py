from sserver.mixin.OptionMixin import OptionMixin


#
# Base Endpoint
#
class BaseEndpoint(OptionMixin):

    #
    # Get
    #
    def get(self):
        return ''

    #
    # Post
    #
    def post(self):
        return ''

    #
    # Put
    #
    def put(self):
        return ''

    #
    # Patch
    #
    def patch(self):
        return ''

    #
    # Delete
    #
    def delete(self):
        return ''