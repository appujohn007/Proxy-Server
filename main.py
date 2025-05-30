import http.server
import socketserver
import ssl
import urllib.request
import urllib.parse
import sys
import os

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # Handle HTTPS connect method for tunneling
        self.send_response(200, "Connection Established")
        self.end_headers()

        try:
            conn = self.connection
            address = self.path.split(":")
            host, port = address[0], int(address[1])

            with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as remote:
                remote.connect((host, port))
                self.connection.setblocking(False)
                remote.setblocking(False)

                while True:
                    rlist, _, _ = select.select([conn, remote], [], [], 1)
                    if conn in rlist:
                        data = conn.recv(8192)
                        if not data:
                            break
                        remote.sendall(data)
                    if remote in rlist:
                        data = remote.recv(8192)
                        if not data:
                            break
                        conn.sendall(data)
        except Exception as e:
            self.send_error(500, str(e))

    def do_GET(self):
        self.proxy_request("GET")

    def do_POST(self):
        self.proxy_request("POST")

    def do_PUT(self):
        self.proxy_request("PUT")

    def do_DELETE(self):
        self.proxy_request("DELETE")

    def proxy_request(self, method):
        try:
            url = self.path
            if not url.startswith('http'):
                url = f"http://{self.headers['Host']}{self.path}"

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else None

            req = urllib.request.Request(
                url,
                data=body,
                headers={k: v for k, v in self.headers.items() if k != 'Host'},
                method=method
            )
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, value in response.getheaders():
                    if key.lower() == "transfer-encoding" and value.lower() == "chunked":
                        continue
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, str(e))

def run(server_class=http.server.ThreadingHTTPServer, handler_class=ProxyHTTPRequestHandler):
    port = int(os.environ.get("PORT", 8000))
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Serving HTTP Proxy on port {port} ...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
