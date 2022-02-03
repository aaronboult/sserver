from sserver.log.Logger import Logger

class Route:
    def __init__(self, url, name, endpoint, **kwargs):
        self.url = url
        self.name = name
        self.endpoint = endpoint


#
# Route
#
def route(*args, **kwargs):
    return Route(*args, **kwargs)