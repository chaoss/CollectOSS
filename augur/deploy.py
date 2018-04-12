from gevent.wsgi import WSGIServer
import augur

http_server = WSGIServer(('', 5001), augur.server.app)
http_server.serve_forever()