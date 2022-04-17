from sserver.server import application, initialize
from sserver.log.Logger import Logger


if __name__ == 'uwsgi_file_server':
    initialize(**{
        'config' : {
        },
    })