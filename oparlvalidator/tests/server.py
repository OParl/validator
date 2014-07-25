# -*- encoding: utf-8 -*-

"""
Example:
s = Server()
s.port  # get the automatically picked port
s.serve({
"/url/path": '{"id":"http://oparl.example.org/url/path"}',
"/another/path": {
"GET":
    {
        'body': '{"id":"http://oparl.example.org/another/path"}',
        'headers': [('X-customHeader', 'headerValue')],
        'status_code': 201
    }
}
})
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import threading
import six
from six.moves import BaseHTTPServer  # pylint: disable=import-error


class Server(object):

    def __init__(self, port=0):
        server_class = BaseHTTPServer.HTTPServer
        self.httpd = server_class(('127.0.0.1', port), Server._HTTPHandler)

        self.port = self.httpd.server_address[1]
        self.httpd.data = {}

        httpd_thread = threading.Thread(target=self.httpd.serve_forever)
        httpd_thread.setDaemon(True)
        httpd_thread.start()

    def __del__(self):
        self.httpd.shutdown()

    def serve(self, data):
        self.httpd.data = data

    class _HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        # pylint: disable=no-init,no-member

        DEFAULT_BODY = ''
        DEFAULT_STATUS_CODE = 200
        DEFAULT_HEADERS = [('Content-Type', 'application/json')]
        ENCODING = 'utf-8'

        def do_OPTIONS(self):
            return self.all_handler()

        def do_HEAD(self):
            return self.all_handler()

        def do_POST(self):
            return self.all_handler()

        def do_PUT(self):
            return self.all_handler()

        def do_DELETE(self):
            return self.all_handler()

        def do_TRACE(self):
            return self.all_handler()

        def do_GET(self):
            return self.all_handler()

        def all_handler(self):
            try:
                response = self.server.data[self.path]

                if isinstance(response, six.string_types):
                    response = {'GET': {'body': response}}

                response.setdefault('body', self.DEFAULT_BODY)
                response.setdefault('status_code', self.DEFAULT_STATUS_CODE)
                response.setdefault('headers', self.DEFAULT_HEADERS)

                self.send_response(response['status_code'])
                for header in response['headers']:
                    self.send_header(header[0], header[1])
                self.end_headers()

                self.wfile.write(response['body'].encode(self.ENCODING))

            except KeyError:
                self.send_response(404)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write('not found'.encode(self.ENCODING))
