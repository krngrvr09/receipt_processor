from utils import regex_patterns
import uuid
import re
from decimal import Decimal
import math

class Receipt:
    """Receipt class to store receipt data and calculate points."""

    id=None
    retailer=None
    purchaseDate=None
    purchaseTime=None
    items=[]
    total=None
    score=None

    def __init__(self, receipt_json):
        """
        Initialize a Receipt object from a JSON object. The JSON object must have the following fields:

        - retailer: The name of the retailer.
        - purchaseDate: The date of the purchase in the format YYYY-MM-DD.
        - purchaseTime: The time of the purchase in the format HH:MM or H:MM.
        - total: The total amount of the purchase in the format (D+).DD.
        - items: A list of items purchased.
        """

        assert "retailer" in receipt_json and \
            self.validPattern("retailer", receipt_json["retailer"])
        self.retailer = receipt_json["retailer"]

        assert "purchaseDate" in receipt_json and \
            self.validPattern("purchaseDate", receipt_json["purchaseDate"])
        self.purchaseDate = receipt_json["purchaseDate"]
        
        assert "purchaseTime" in receipt_json and \
            self.validPattern("purchaseTime", receipt_json["purchaseTime"])
        self.purchaseTime = receipt_json["purchaseTime"]
        
        assert "total" in receipt_json and \
            self.validPattern("total", receipt_json["total"])
        self.total = receipt_json["total"]

        assert "items" in receipt_json and \
            isinstance(receipt_json["items"], list) and \
            len(receipt_json["items"])>0
        for item in receipt_json["items"]:
            self.items.append(Item(item))

        self.id = str(uuid.uuid4())


    def validPattern(self, field, value):
        """Make sure the value matches the regex pattern for the field."""

        return re.match(regex_patterns[field], value)


    def getPointsFromRetailer(self):
        """One point for every alphanumeric character in the retailer name."""

        alphanumeric_count = sum(c.isalnum() for c in self.retailer)
        return alphanumeric_count


    def getPointsFromTotal(self):
        """
        50 points if the total is a round dollar amount with no cents.
        25 points if the total is a multiple of 0.25.
        """

        points=0
        cent_val = int(self.total.split(".")[1])
        if cent_val==0:
            points+=50
        if cent_val in [0,25,50,75]:
            points+=25
        
        return points


    def getPointsFromItems(self):
        """
        5 points for every two items on the receipt.
        If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.

        Using Decimal to avoid floating point errors.
        """
        
        points=0
        item_count = len(self.items)
        points+=(item_count//2)*5
        for item in self.items:
            if len(item.shortDescription.strip())%3==0:
                decimal_value = Decimal(item.price)
                points+=math.ceil(decimal_value*Decimal(0.2))
        return points


    def getPointsFromDate(self):
        """
        6 points if the day in the purchase date is odd.
        """

        points=0
        date_val = int(self.purchaseDate.split("-")[2])
        if date_val%2==1:
            points=6
        return points


    def getPointsFromTime(self):
        """
        10 points if the time of purchase is after 2:00pm and before 4:00pm.
        """

        points=0
        hour_val = int(self.purchaseTime.split(":")[0])
        minute_val = int(self.purchaseTime.split(":")[1])
        if hour_val==15 or (hour_val==14 and minute_val>0):
            points=10
        return points


    def calculateScore(self):
        """
        Calculates the points earned from the receipt data.
        """
        points=0
        points+=self.getPointsFromRetailer()
        points+=self.getPointsFromTotal()
        points+=self.getPointsFromItems()
        points+=self.getPointsFromDate()
        points+=self.getPointsFromTime()
        self.score = points


    def getScore(self):
        """
        If the score has not been calculated, calculate it. Return the score.
        """

        if self.score is None:
            self.calculateScore()
        return self.score

class Item:
    """Item class to store item data."""

    shortDescription=None
    price=None

    def __init__(self, item_json):
        """
        Initialize an Item object from a JSON object. The JSON object must have the following fields:

        - shortDescription: A short description of the item.
        - price: The price of the item in the format (D+).DD.
        """

        assert "shortDescription" in item_json and \
            self.validPattern("shortDescription", item_json["shortDescription"])
        self.shortDescription = item_json["shortDescription"]

        assert "price" in item_json and \
            self.validPattern("price", item_json["price"])
        self.price = item_json["price"]
    
    
    def validPattern(self, field, value):
        """Make sure the value matches the regex pattern for the field."""
        return re.match(regex_patterns[field], value)