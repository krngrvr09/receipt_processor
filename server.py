from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import uuid
from decimal import Decimal
import math
data_store = {}

regex_patterns = {
    'retailer': r'^[\ \S]+$',
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

def getPointsFromRetailer(retailer):
    alphanumeric_count = sum(c.isalnum() for c in retailer)
    print("alphanumeric_count: ", alphanumeric_count)
    return alphanumeric_count

def getPointsFromTotal(total):
    points=0
    cent_val = int(total.split(".")[1])
    if cent_val==0:
        points+=50
    if cent_val in [0,25,50,75]:
        points+=25
    
    return points

def getPointsFromItems(items):
    points=0
    item_count = len(items)
    points+=(item_count//2)*5
    for item in items:
        if len(item["shortDescription"].strip())%3==0:
            decimal_value = Decimal(item["price"])
            points+=math.ceil(decimal_value*Decimal(0.2))
    return points

def getPointsFromDate(purchaseDate):
    points=0
    date_val = int(purchaseDate.split("-")[2])
    if date_val%2==1:
        points=6
    return points

def getPointsFromTime(purchaseTime):
    points=0
    hour_val = int(purchaseTime.split(":")[0])
    minute_val = int(purchaseTime.split(":")[1])
    if hour_val==15 or (hour_val==14 and minute_val>0):
        points=10
    return points


def getPoints(receipt_data):
    res=0
    res+=getPointsFromRetailer(receipt_data['retailer'])
    res+=getPointsFromTotal(receipt_data['total'])
    res+=getPointsFromItems(receipt_data['items'])
    res+=getPointsFromDate(receipt_data['purchaseDate'])
    res+=getPointsFromTime(receipt_data['purchaseTime'])
    return res

# Create a custom request handler by subclassing BaseHTTPRequestHandler
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/receipts/') and self.path.endswith('/points'):
            receipt_id = self.path.split('/')[2]
            print(receipt_id)
            if receipt_id in data_store:
                points = data_store[receipt_id]['points']
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
            receipt_id = str(uuid.uuid4())
            # Store the receipt data in the data store
            data_store[receipt_id] = {
                'retailer': receipt_data['retailer'],
                'purchaseDate': receipt_data['purchaseDate'],
                'purchaseTime': receipt_data['purchaseTime'],
                'items': receipt_data['items'],
                'total': receipt_data['total'],
                'points': getPoints(receipt_data)  # Replace with actual points calculation logic
            }

            response_data = {'id': receipt_id}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
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
