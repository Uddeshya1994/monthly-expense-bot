from fastapi import FastAPI
from pydantic import BaseModel
import csv
import os
from expense_parser import parse_expense

app = FastAPI()

CSV_FILE = "expenses.csv"

class Expense(BaseModel):
    text: str
    person: str

# Create CSV if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Amount", "Category", "Description", "Person"])

@app.post("/add-expense")
def add_expense(expense: Expense):
    parsed = parse_expense(expense.text)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            parsed["date"],
            parsed["amount"],
            parsed["category"],
            parsed["description"],
            expense.person
        ])

    return {
        "status": "saved",
        "data": parsed
    }
