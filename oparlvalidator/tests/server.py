# -*- encoding: utf-8 -*-

"""
Example:
server = Server()
server.port  # get the automatically picked port
server.serve({
'/url/path': '{"id": "http://oparl.example.org/url/path"}',
'/another/path': {
'GET':
    {
        'body': '{"id": "http://oparl.example.org/another/path"}',
        'headers': [('X-customHeader', 'headerValue')],
        'status_code': 201
    }
}
})
"""

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import argparse
import threading
# pylint: disable=import-error,redefined-builtin
from six.moves import BaseHTTPServer, input


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

    def log_message(self, *_):
        entry = vars(self)
        entry['url'] = self.server.url + self.path
        self.server.log.append(entry)
        return entry

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

    def __init__(self, host='127.0.0.1', port=0, handler=_HTTPHandler):
        self.httpd = BaseHTTPServer.HTTPServer((host, port), handler)
        self.host, self.port = self.httpd.server_address
        self.httpd.url = 'http://{}:{}'.format(self.host, self.port)
        self.httpd.data = {}
        self.httpd.log = []

        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.setDaemon(True)
        self.thread.start()

    def __del__(self):
        self.shutdown()

    def serve(self, data):
        self.httpd.data = data

    def shutdown(self):
        self.httpd.shutdown()

    @property
    def url(self):
        return self.httpd.url

    @property
    def log(self):
        return self.httpd.log


def run():
    parser = argparse.ArgumentParser(description='Starts a test server.')
    parser.add_argument('--host', default='127.0.0.1',
                        help='The host name or IP address')
    parser.add_argument('--port', default=0,
                        help='The port number')
    args = parser.parse_args()

    class Handler(_HTTPHandler):
        # pylint: disable=no-init
        def log_message(self, *args):
            entry = _HTTPHandler.log_message(self, *args)
            print(entry)

    server = Server(host=args.host, port=args.port, handler=Handler)
    paths = {}
    root = 'oparlvalidator/tests/testdata/'
    for filename in os.listdir(root):
        with open(os.path.join(root, filename)) as filehandle:
            body = filehandle.read().replace(
                'https://oparl.example.org', server.url)
            paths['/' + filename] = {'GET': {'body': body}}
    print('Server started at', server.url)
    server.serve(paths)
    input('Hit return to quit.\n')
