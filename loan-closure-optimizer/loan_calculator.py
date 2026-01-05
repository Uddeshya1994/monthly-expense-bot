def calculate_emi(principal, annual_rate, years):
    r = annual_rate / (12 * 100)
    n = years * 12
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return round(emi, 2)


def loan_schedule(
    principal,
    annual_rate,
    emi,
    extra_monthly=0,
    lump_sum=0,
    lump_sum_month=0
):
    r = annual_rate / (12 * 100)
    balance = principal
    total_interest = 0
    month = 0
    schedule = []

    while balance > 0:
        month += 1
        interest = balance * r
        principal_payment = emi - interest + extra_monthly

        # One-time lump sum payment
        if month == lump_sum_month:
            principal_payment += lump_sum

        if principal_payment > balance:
            principal_payment = balance

        balance -= principal_payment
        total_interest += interest

        schedule.append((month, round(balance, 2)))

    return month, round(total_interest, 2), schedule
