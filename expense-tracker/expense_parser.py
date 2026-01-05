import re
from datetime import datetime

def parse_expense(text):
    text = text.lower()

    # Extract amount
    amount_match = re.search(r'\d+', text)
    amount = int(amount_match.group()) if amount_match else 0

    # Category rules
    categories = {
        "uber": "Travel",
        "ola": "Travel",
        "bus": "Travel",
        "train": "Travel",
        "swiggy": "Food",
        "zomato": "Food",
        "dinner": "Food",
        "lunch": "Food",
        "breakfast": "Food",
        "vegetable": "Groceries",
        "milk": "Groceries",
        "fruit": "Groceries",
        "electricity": "Bills",
        "rent": "Bills",
        "netflix": "Entertainment",
        "amazon": "Shopping",
        "flipkart": "Shopping",
        "doctor": "Medical",
        "medicine": "Medical"
    }

    category = "Misc"
    for key, value in categories.items():
        if key in text:
            category = value
            break

    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "amount": amount,
        "category": category,
        "description": text
    }
