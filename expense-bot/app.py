import streamlit as st
import pandas as pd
from datetime import datetime
import os

EXPENSE_FILE = "data/expenses.csv"
BUDGET_FILE = "data/budgets.csv"

# ---------- Loaders ----------
def load_expenses():
    if os.path.exists(EXPENSE_FILE):
        return pd.read_csv(EXPENSE_FILE)
    return pd.DataFrame(columns=[
        "date", "amount", "category", "paid_by",
        "payment_mode", "expense_type", "recurring", "notes"
    ])

def load_budgets():
    if os.path.exists(BUDGET_FILE):
        return pd.read_csv(BUDGET_FILE)
    return pd.DataFrame(columns=["category", "monthly_budget"])

def save_expenses(df):
    df.to_csv(EXPENSE_FILE, index=False)

def save_budgets(df):
    df.to_csv(BUDGET_FILE, index=False)

# ---------- UI ----------
st.set_page_config(page_title="Monthly Expense Bot", layout="centered")
st.title("💰 Monthly Expense Bot")
st.caption("Shared by Megha & Uddeshya")

expenses = load_expenses()
budgets = load_budgets()

# ---------- Add Expense ----------
st.subheader("➕ Add Expense")

with st.form("expense_form"):
    amount = st.number_input("Amount (₹)", min_value=1, step=1)
    category = st.selectbox("Category", budgets["category"].tolist())
    paid_by = st.radio("Paid By", ["Uddeshya", "Megha"])
    payment_mode = st.selectbox(
        "Payment Mode", ["UPI", "Cash", "Credit Card", "Debit Card", "Net Banking"]
    )
    expense_type = st.radio("Expense Type", ["Need", "Want"])
    recurring = st.selectbox("Recurring?", ["No", "Yes"])
    notes = st.text_input("Notes (optional)")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "category": category,
            "paid_by": paid_by,
            "payment_mode": payment_mode,
            "expense_type": expense_type,
            "recurring": recurring,
            "notes": notes
        }
        expenses = pd.concat([expenses, pd.DataFrame([new_row])], ignore_index=True)
        save_expenses(expenses)
        st.success("Expense added successfully ✅")

# ---------- SUMMARY SECTION ----------
st.divider()
st.subheader("📊 Quick Summary")

today = datetime.now().strftime("%Y-%m-%d")
current_month = datetime.now().strftime("%Y-%m")

today_df = expenses[expenses["date"] == today]
month_df = expenses[expenses["date"].str.startswith(current_month)]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📅 Today Total", f"₹{today_df['amount'].sum():,.0f}")

with col2:
    st.metric("📆 Month Total", f"₹{month_df['amount'].sum():,.0f}")

with col3:
    diff = (
        month_df[month_df["paid_by"] == "Uddeshya"]["amount"].sum()
        - month_df[month_df["paid_by"] == "Megha"]["amount"].sum()
    )
    if diff > 0:
        st.metric("⚖️ Settlement", f"Megha owes ₹{diff:,.0f}")
    elif diff < 0:
        st.metric("⚖️ Settlement", f"Uddeshya owes ₹{abs(diff):,.0f}")
    else:
        st.metric("⚖️ Settlement", "All Settled ✅")



# ---------- Monthly Split ----------
st.markdown("**👫 Monthly Split**")
st.write(
    "Uddeshya:",
    f"₹{month_df[month_df['paid_by'] == 'Uddeshya']['amount'].sum():,.0f}"
)
st.write(
    "Megha:",
    f"₹{month_df[month_df['paid_by'] == 'Megha']['amount'].sum():,.0f}"
)

# ---------- Export Section ----------
st.divider()
st.subheader("📤 Export Data")

export_col1, export_col2 = st.columns(2)

with export_col1:
    st.download_button(
        label="⬇️ Export Current Month (CSV)",
        data=month_df.to_csv(index=False),
        file_name=f"expenses_{current_month}.csv",
        mime="text/csv"
    )

with export_col2:
    st.download_button(
        label="⬇️ Export Full History (CSV)",
        data=expenses.to_csv(index=False),
        file_name="expenses_full_history.csv",
        mime="text/csv"
    )

# ---------- Budget Overview ----------
st.divider()
st.subheader("🎯 Monthly Budget Overview")

for _, row in budgets.iterrows():
    cat = row["category"]
    budget = row["monthly_budget"]
    spent = month_df[month_df["category"] == cat]["amount"].sum()
    remaining = budget - spent

    if spent > budget:
        st.error(f"🔴 {cat}: ₹{spent:,.0f} / ₹{budget:,.0f}  (Exceeded by ₹{abs(remaining):,.0f})")
    else:
        st.success(f"🟢 {cat}: ₹{spent:,.0f} / ₹{budget:,.0f}  (Remaining ₹{remaining:,.0f})")

# ---------- Budget Editor ----------
st.divider()
st.subheader("✏️ Edit Monthly Budgets")

edited_budgets = st.data_editor(
    budgets,
    num_rows="dynamic",
    use_container_width=True
)

if st.button("Save Budgets"):
    save_budgets(edited_budgets)
    st.success("Budgets updated successfully 🔄")
