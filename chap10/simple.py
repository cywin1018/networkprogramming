from wsgiref.simple_server import make_server

def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, response_headers)
    response = ['Hello World!\n'.encode('utf-8')]
    return response

if __name__ == '__main__':
    httpd = make_server('', 8000, simple_app)
    host,port = httpd.socket.getsockname()
    print('Serving on', host, 'port', port)
    httpd.serve_forever()
