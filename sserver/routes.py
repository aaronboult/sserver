from sserver.log.Logger import Logger


#
# Route
#
class Route:
    def __init__(self, url, name, endpoint, **kwargs):
        self.url = url
        self.name = name
        self.endpoint = endpoint
    
    def __str__(self):
        return f'<{self.__class__.__name__} url="{self.url}">'


#
# Route
#
def route(*args, **kwargs):
    return Route(*args, **kwargs)