from log.Logger import Logger

def application(environment, start_response):

    Logger.log('Environment', environment)

    try:
        pass
    
    except Exception as e:
        pass

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"Hello World"]