from http.server import BaseHTTPRequestHandler, HTTPServer

# Create a custom request handler by subclassing BaseHTTPRequestHandler
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/receipts/') and self.path.endswith('/points'):
            # Handle GET requests
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Hello, GET request!')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"message": "Not Found"}')

    def do_POST(self):
        if self.path == "/receipts/process":
            # Handle POST requests
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Hello, POST request!')
            print(f'Received POST data: {post_data.decode()}')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"message": "Not Found"}')

# Set up the server
server_address = ('', 8000)  # Empty string indicates localhost
httpd = HTTPServer(server_address, MyRequestHandler)

# Start the server
print('Server started on http://localhost:8000')
httpd.serve_forever()
