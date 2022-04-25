#
# Internal Config File For SServer
#


CONFIG_CACHE_KEY = 'sserver.config'


SSERVER_CONFIG = {
}


PROJECT_DEFAULT_CONFIG = {
    'APP_FOLDER'                 : 'apps',
    'CACHE_HOST'                 : 'localhost',
    'CACHE_PORT'                 : 6379,
    'CACHE_DECODE_STRINGS'       : True,
    'APP_NAME_REGEX'             : '^([A-Za-z_]*)\.([A-Za-z_]*)\.([A-Za-z_]*)',
    'PREFIX_ROUTE_WITH_APP_NAME' : True,
}


APP_DEFAULT_CONFIG = {
    'TEMPLATE_FOLDER' : 'templates',
}