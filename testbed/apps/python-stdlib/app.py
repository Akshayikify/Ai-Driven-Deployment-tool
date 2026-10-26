import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')


HTTPServer(('0.0.0.0', int(os.environ.get('PORT', 8000))), H).serve_forever()
