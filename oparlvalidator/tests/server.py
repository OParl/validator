# -*- encoding: utf-8 -*-

"""
Example:
s = Server()
s.port  # get the automatically picked port
s.serve({
'/url/path': '{"id":"http://oparl.example.org/url/path"}',
'/another/path': {
'GET':
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
from six.moves import BaseHTTPServer  # pylint: disable=import-error


class _HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # pylint: disable=no-init,no-member

    DEFAULT_RESPONSE = {
        'body': '',
        'status_code': 200,
        'headers': [('Content-Type', 'application/json')]
    }
    ENCODING = 'utf-8'

    def do_OPTIONS(self):
        return self._handler()

    def do_HEAD(self):
        return self._handler()

    def do_POST(self):
        return self._handler()

    def do_PUT(self):
        return self._handler()

    def do_DELETE(self):
        return self._handler()

    def do_TRACE(self):
        return self._handler()

    def do_GET(self):
        return self._handler()

    def _send_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('Not Found'.encode(self.ENCODING))

    def _send_501(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write('Not Implemented'.encode(self.ENCODING))

    def _send_response(self, data):
        response = self.DEFAULT_RESPONSE
        response.update(data)

        self.send_response(response['status_code'])
        for (name, value) in response['headers']:
            self.send_header(name, value)
        self.end_headers()

        self.wfile.write(response['body'].encode(self.ENCODING))

    def _handler(self):
        if self.path not in self.server.data:
            self._send_404()
            return

        response = self.server.data[self.path]
        if not isinstance(response, dict):
            response = {'GET': {'body': response}}

        if self.command not in response:
            self._send_501()
            return

        self._send_response(response[self.command])


class Server(object):

    def __init__(self, host='127.0.0.1', port=0):
        self.httpd = BaseHTTPServer.HTTPServer((host, port),
                                               _HTTPHandler)
        self.host, self.port = self.httpd.server_address
        self.httpd.data = {}

        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.setDaemon(True)
        self.thread.start()

    def __del__(self):
        self.shutdown()

    def serve(self, data):
        self.httpd.data = data

    def shutdown(self):
        self.httpd.shutdown()
