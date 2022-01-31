from sserver.urls import route

urls = [
    route('/', 'index', 'index'),
    route('/test', 'test', 'test'),
]