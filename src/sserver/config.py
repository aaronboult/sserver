#
# Internal Config File For SServer
#


SSERVER_CONFIG = {
    'APP_NAME_REGEX' : '^([A-Za-z_]*)\.([A-Za-z_]*)\.([A-Za-z_]*)',
    'PREFIX_ROUTE_WITH_APP_NAME' : True,
}


PROJECT_DEFAULT_CONFIG = {
    'APP_FOLDER' : 'apps',
    'CACHE_HOST' : 'localhost',
    'CACHE_PORT' : 6379,
    'CACHE_DECODE_STRINGS' : True,
}


APP_DEFAULT_CONFIG = {
    'templates' : {
        'TEMPLATE_FOLDER' : 'templates',
    },
}