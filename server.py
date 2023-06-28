from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from receipt import Receipt

# The data store is created at the module level, so that
# it is accessible from multiple request handlers if we choose
# to scale up our system by adding more request handlers
data_store = {}


class MyRequestHandler(BaseHTTPRequestHandler):

    def send_reply(self, code, response=None, headers=None):
        self.send_response(code)
        if not headers:
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        else:
            for header, value in headers.items():
                self.send_header(header, value)
                self.end_headers()
        if response is not None:
            self.wfile.write(json.dumps(response).encode())
                

    def do_GET(self):
        if self.path.startswith('/receipts/') and self.path.endswith('/points'):
            receipt_id = self.path.split('/')[2]
            # print(receipt_id)
            if receipt_id in data_store:
                points = data_store[receipt_id].getScore()
                response_data = {'points': points}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"message": "No receipt found for that id"}')
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
            try:
                receipt_data = json.loads(post_data.decode())
            except json.JSONDecodeError:
                response = {'message': 'The receipt is invalid'}
                self.send_reply(400, response)
                return
            
            receipt = Receipt(receipt_data)
            receipt.calculateScore()

            data_store[receipt.id] = receipt

            response = {'id': receipt.id}
            headers = {'Content-type': 'application/json'}
            self.send_reply(200, response, headers)
            
        else:
            error_message = "Not Found"
            response = {'message': error_message}
            headers = {'Content-type': 'application/json'}
            self.send_reply(404, response, headers)

# Set up the server
server_address = ('', 8000)  # Empty string indicates localhost
httpd = HTTPServer(server_address, MyRequestHandler)

# Start the server
print('Server started on http://localhost:8000')
httpd.serve_forever()
