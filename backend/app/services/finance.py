from math import pow


def calculate_finance(loan_amount: float, annual_rate: float, repayment_years: int, moratorium_months: int = 0) -> dict:
    if loan_amount <= 0 or annual_rate < 0 or repayment_years <= 0 or moratorium_months < 0:
        raise ValueError("Loan amount and repayment period must be positive; interest and moratorium cannot be negative.")
    months = repayment_years * 12
    rate = annual_rate / 1200
    emi = loan_amount / months if rate == 0 else loan_amount * rate * pow(1 + rate, months) / (pow(1 + rate, months) - 1)
    total = emi * months
    return {"loan_amount": round(loan_amount, 2), "annual_interest_rate": annual_rate, "repayment_months": months,
            "moratorium_months": moratorium_months, "monthly_emi": round(emi, 2), "total_repayment": round(total, 2),
            "total_interest": round(total - loan_amount, 2), "disclaimer": "Indicative - subject to applicable scheme/channel partner terms."}
