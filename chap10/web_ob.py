from pprint import pformat
from wsgiref.simple_server import make_server
import time, webob

def app(environ, start_response):
  request = webob.Request(environ)
  if environ['REQUEST_METHOD'] != 'GET':
    response = webob.Response('501 Not Implemented',status=501 )
  elif request.domain != '127.0.0.1' or request.path != '/':
      response = webob.Response('404 Not Found', status=404)
      #Looking at the path without its trailing query string
  else:
      response = webob.Response(time.ctime())
      # Response Object랑 content types and encoding을 알려준다.
  return response(environ, start_response)

if __name__ == '__main__':
    httpd = make_server('', 8000, app)
    host,port = httpd.socket.getsockname()
    print('Serving on',host,'port',port)
    httpd.serve_forever()