from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from receipt import Receipt


# The data store is created at the module level, so that
# it is accessible from multiple request handlers if we choose
# to scale up our system by adding more request handlers
data_store = {}


class MyRequestHandler(BaseHTTPRequestHandler):

    def send_reply(self, code, response=None, headers=None):
        """
        Wrapper function to send a reply to the client.

        Args:
            code (int): The HTTP status code to send.
            response (dict): The response to send. If None, no response body is sent.
            headers (dict): A dictionary of headers to send. If None, the Content-type header is set to application/json.
        """
        
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
        """
        Handle GET requests. 
        The only GET request that is supported is /receipts/<id>/points.
        """

        if self.path.startswith('/receipts/') and self.path.endswith('/points'):
            receipt_id = self.path.split('/')[2]
            if receipt_id not in data_store:
                response = {'message': 'No receipt found for that id'}
                self.send_reply(404, response)
                return
            
            points = data_store[receipt_id].getScore()
            response = {'points': points}
            self.send_reply(200, response)
        else:
            response = {'message': 'Not Found'}
            self.send_reply(404, response)


    def do_POST(self):
        """
        Handle POST requests.
        The only POST request that is supported is /receipts/process.
        """

        if self.path == "/receipts/process":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                receipt_data = json.loads(post_data.decode())
                receipt = Receipt(receipt_data)
                receipt.calculateScore()
            except Exception as e:
                response = {'message': 'The receipt is invalid'}
                self.send_reply(400, response)
                return            

            data_store[receipt.id] = receipt

            response = {'id': receipt.id}
            self.send_reply(200, response)
        else:
            error_message = "Not Found"
            response = {'message': error_message}
            self.send_reply(404, response)

# Set up the server
server_address = ('', 8000)  # Empty string indicates localhost
httpd = HTTPServer(server_address, MyRequestHandler)

# Start the server
print('Server started on http://localhost:8000')
httpd.serve_forever()
