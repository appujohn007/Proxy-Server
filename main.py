import http.server
import socketserver
import socket
import select
import urllib.request
import urllib.parse
import sys
import os

class ProxyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_CONNECT(self):
        # Handle HTTPS CONNECT method for tunneling
        try:
            host, port = self.path.split(":")
            port = int(port)
            with socket.create_connection((host, port)) as upstream:
                self.send_response(200, "Connection Established")
                self.end_headers()
                self._tunnel(self.connection, upstream)
        except Exception as e:
            self.send_error(500, f"CONNECT error: {e}")

    def _tunnel(self, client_sock, upstream_sock):
        sockets = [client_sock, upstream_sock]
        try:
            while True:
                rlist, _, _ = select.select(sockets, [], [], 10)
                if not rlist:
                    break
                for s in rlist:
                    data = s.recv(8192)
                    if not data:
                        return
                    (upstream_sock if s is client_sock else client_sock).sendall(data)
        except Exception:
            pass  # connection closed

    def do_COMMAND(self):
        self.proxy_request(self.command)

    def do_GET(self):
        self.do_COMMAND()

    def do_POST(self):
        self.do_COMMAND()

    def do_PUT(self):
        self.do_COMMAND()

    def do_DELETE(self):
        self.do_COMMAND()

    def do_OPTIONS(self):
        self.do_COMMAND()

    def do_HEAD(self):
        self.do_COMMAND()

    def proxy_request(self, method):
        try:
            if self.path == "/" or not self.path:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(
                    b"Python Forward Proxy is running.\n"
                    b"Use this server as an HTTP proxy (curl -x http://<host>:<port> https://example.com).\n"
                )
                return

            url = self.path
            if not url.startswith("http"):
                url = f"http://{self.headers['Host']}{self.path}"

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length else None

            # Prepare headers for the proxied request
            headers = dict(self.headers)
            headers.pop("Host", None)
            headers.pop("Proxy-Connection", None)
            headers.pop("Connection", None)

            req = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method=method
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                self.send_response(response.status)
                for key, value in response.getheaders():
                    # Avoid chunked encoding to simplify things
                    if key.lower() == "transfer-encoding" and value.lower() == "chunked":
                        continue
                    self.send_header(key, value)
                self.end_headers()
                chunk = response.read(8192)
                while chunk:
                    self.wfile.write(chunk)
                    chunk = response.read(8192)
        except Exception as e:
            self.send_error(500, f"Proxy error: {e}")

def run():
    port = int(os.environ.get("PORT", 8080))
    server_address = ("", port)
    handler_class = ProxyHTTPRequestHandler
    httpd = socketserver.ThreadingTCPServer(server_address, handler_class)
    print(f"Serving HTTP proxy on port {port} ...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
