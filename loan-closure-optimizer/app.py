import streamlit as st
import matplotlib.pyplot as plt
from loan_calculator import calculate_emi, loan_schedule

st.title("🏦 Loan Closure Optimizer")

# Inputs
loan_amount = st.number_input("Loan Amount (₹)", min_value=10000, value=1000000)
interest_rate = st.number_input("Interest Rate (%)", value=8.5)
tenure_years = st.number_input("Loan Tenure (Years)", value=20)

extra_monthly = st.number_input(
    "Extra Monthly Payment (₹)",
    min_value=0,
    value=0
)

lump_sum = st.number_input(
    "One-time Lump Sum Payment (₹)",
    min_value=0,
    value=0
)

lump_sum_month = 0
if lump_sum > 0:
    lump_sum_month = st.number_input(
        "Lump Sum Payment Month",
        min_value=1,
        max_value=tenure_years * 12,
        value=12
    )

# EMI
emi = calculate_emi(loan_amount, interest_rate, tenure_years)
st.subheader(f"💸 Monthly EMI: ₹{emi}")

# Normal Loan
normal_months, normal_interest, _ = loan_schedule(
    loan_amount, interest_rate, emi
)

# Optimized Loan
opt_months, opt_interest, schedule = loan_schedule(
    loan_amount,
    interest_rate,
    emi,
    extra_monthly=extra_monthly,
    lump_sum=lump_sum,
    lump_sum_month=lump_sum_month
)

# Results
st.markdown("### 📊 Loan Comparison")

st.write(f"📆 Original Tenure: {normal_months} months")
st.write(f"📉 New Tenure: {opt_months} months")
st.write(f"⏳ Tenure Reduced: {normal_months - opt_months} months")

st.write(f"💰 Interest without optimization: ₹{normal_interest}")
st.write(f"💰 Interest with optimization: ₹{opt_interest}")
st.write(f"✅ Interest Saved: ₹{normal_interest - opt_interest}")

# Chart
months = [m for m, b in schedule]
balances = [b for m, b in schedule]

plt.figure()
plt.plot(months, balances)
plt.xlabel("Month")
plt.ylabel("Outstanding Balance (₹)")
plt.title("Outstanding Loan Balance Over Time")
st.pyplot(plt)
