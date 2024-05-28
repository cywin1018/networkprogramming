from pprint import pformat

def app(environ,start_response):
    headers = {'Content-Type': 'text/plain; charset=utf-8'}
    start_response('200 OK', list(headers.items()))
    yield 'Here is the WSGI environment:\n\n'.enocde('utf-8')
    yield pformat(environ).encode('utf-8')

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('localhost', 8080, app)
        print("Serving on port 8080...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Goodbye.")