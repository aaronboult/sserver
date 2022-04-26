#
# Internal Config File For SServer
#


CONFIG_CACHE_KEY = 'sserver.config'


SSERVER_CONFIG = {
}


PROJECT_DEFAULT_CONFIG = {
    'app_folder'                 : 'apps',
    'cache_host'                 : 'localhost',
    'cache_port'                 : 6379,
    'cache_decode_strings'       : True,
    'prefix_route_with_app_name' : True,
}


APP_DEFAULT_CONFIG = {
    'TEMPLATE_FOLDER' : 'templates',
}