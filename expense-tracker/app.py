import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# ----------------- BASIC CONFIG -----------------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰 Personal Expense Tracker (WhatsApp Based)")

DATA_FILE = "expenses.csv"

# ----------------- INIT DATA -----------------
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=[
        "Date", "Person", "Amount", "Category", "Description"
    ])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# ----------------- ADD EXPENSE -----------------
st.subheader("➕ Add Expense")

col1, col2 = st.columns(2)

with col1:
    text = st.text_input("Paste WhatsApp message here",
                         placeholder="Paid 320 for vegetables")

with col2:
    person = st.selectbox("Who spent?", ["You", "Wife"])

if st.button("Save Expense"):
    if text.strip() == "":
        st.error("Please enter expense text")
    else:
        # Extract amount
        amount_match = re.search(r"\d+", text)
        amount = int(amount_match.group()) if amount_match else 0

        # Category rules
        rules = {
            "uber": "Travel",
            "ola": "Travel",
            "bus": "Travel",
            "train": "Travel",
            "swiggy": "Food",
            "zomato": "Food",
            "lunch": "Food",
            "dinner": "Food",
            "vegetable": "Groceries",
            "milk": "Groceries",
            "fruit": "Groceries",
            "electricity": "Bills",
            "rent": "Bills",
            "amazon": "Shopping",
            "flipkart": "Shopping",
            "doctor": "Medical",
            "medicine": "Medical"
        }

        category = "Misc"
        for key, value in rules.items():
            if key in text.lower():
                category = value
                break

        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Person": person,
            "Amount": amount,
            "Category": category,
            "Description": text
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        st.success(f"Saved ₹{amount} under {category}")

# ----------------- DASHBOARD -----------------
st.divider()
st.subheader("📊 Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Total Spend", f"₹{df['Amount'].sum()}")
col2.metric("Your Spend", f"₹{df[df.Person=='You']['Amount'].sum()}")
col3.metric("Wife Spend", f"₹{df[df.Person=='Wife']['Amount'].sum()}")

st.subheader("📂 Category-wise Spend")
st.bar_chart(df.groupby("Category")["Amount"].sum())

st.subheader("👫 Person-wise Spend")
st.bar_chart(df.groupby("Person")["Amount"].sum())

st.subheader("📄 All Expenses")
st.dataframe(df.sort_values(by="Date", ascending=False))
