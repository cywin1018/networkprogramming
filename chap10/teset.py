from urllib.parse import parse_qs
# cgi 가 3.13 버전에서는 망해서? parse_qs를 사용하였다.
form = b'''
<html>
    <head>
        <title>Hello User!</title>
    </head>
    <body>
        <form method="post">
            <label>Hello</label>
            <input type="text" name="name">
            <input type="submit" value="Go">
        </form>
    </body>
</html>
'''

def app(environ, start_response):
    html = form

    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        request_body = environ['wsgi.input'].read(request_body_size)
        post_params = parse_qs(request_body.decode('utf-8'))

        name = post_params.get('name', [''])[0]
        html = ('Hello, ' + name + '!').encode('utf-8')

    start_response('200 OK', [('Content-Type', 'text/html')])
    return [html]

if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8080, app)
        print('Serving on port 8080...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
