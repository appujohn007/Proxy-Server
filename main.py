from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import requests

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = self.path
        if not url.startswith('http'):
            url = f'http://{self.headers["Host"]}{self.path}'
        print(f"Fetching: {url}")
        r = requests.get(url, headers=self.headers, stream=True)
        self.send_response(r.status_code)
        for key, value in r.headers.items():
            if key.lower() == "transfer-encoding":
                continue
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(r.content)

    def do_POST(self):
        url = self.path
        if not url.startswith('http'):
            url = f'http://{self.headers["Host"]}{self.path}'
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        r = requests.post(url, data=post_data, headers=self.headers, stream=True)
        self.send_response(r.status_code)
        for key, value in r.headers.items():
            if key.lower() == "transfer-encoding":
                continue
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(r.content)

def run(server_class=HTTPServer, handler_class=ProxyHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting proxy on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
