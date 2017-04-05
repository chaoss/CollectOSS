from gevent.wsgi import WSGIServer
import ghdata

http_server = WSGIServer(('', 5001), ghdata.server.app)
http_server.serve_forever()