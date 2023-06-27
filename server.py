from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re

regex_patterns = {
    'retailer': r'^^[\w\s\-]+$',
    'purchaseDate': r'^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$',
    'purchaseTime': r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$',
    'total': r'^\d+\.\d{2}$',
    'shortDescription': r'^[\w\s\-]+$',
    'price': r'^\d+\.\d{2}$'
}

def validateItem(item):
    required_fields = ['shortDescription', 'price']
    missing_fields = [field for field in required_fields if field not in item]
    if missing_fields:
        return False
    for field in required_fields:
        if field in regex_patterns and not re.match(regex_patterns[field], item[field]):
            return False
    return True

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
            try:
                receipt_data = json.loads(post_data.decode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"message": " The receipt is invalid"}')
                return
            
            # Check if required fields are present
            required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
            missing_fields = [field for field in required_fields if field not in receipt_data]
            
            if missing_fields:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_message = "The receipt is invalid"
                error_data = f'Missing fields: {", ".join(missing_fields)}'
                self.wfile.write(json.dumps({'message': error_message,'data': error_data}).encode())
                return
            
            for field in required_fields:
                if field in regex_patterns and not re.match(regex_patterns[field], receipt_data[field]):
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_message = "The receipt is invalid"
                    error_data = f'Invalid field: {field}'
                    self.wfile.write(json.dumps({'message': error_message,'data': error_data}).encode())
                    return
                elif field == "items":
                    if len(receipt_data[field]) == 0:
                        self.send_response(400)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        error_message = "The receipt is invalid"
                        error_data = f'Invalid field: {field}'
                        self.wfile.write(json.dumps({'message': error_message,'data': error_data}).encode())
                        return
                    
                    for item in receipt_data[field]:
                        if not validateItem(item):
                            self.send_response(400)
                            self.send_header('Content-type', 'application/json')
                            self.end_headers()
                            error_message = "The receipt is invalid"
                            error_data = f'Invalid field: {field}'
                            self.wfile.write(json.dumps({'message': error_message,'data': error_data}).encode())
                            return
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
