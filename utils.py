"""
Regex patterns for validating input data.
"""
regex_patterns = {
    'retailer': r'^[\ \S]+$',
    'purchaseDate': r'^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$',
    'purchaseTime': r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$',
    'total': r'^\d+\.\d{2}$',
    'shortDescription': r'^[\w\s\-]+$',
    'price': r'^\d+\.\d{2}$'
}
