from typing import Any

from app.rules.scheme_rules import SCHEMES

REQUIRED_FIELDS = ("age", "purpose", "annual_income", "social_category", "caste_certificate", "project_cost")


def _missing(profile: dict[str, Any], field: str) -> bool:
    return field not in profile or profile[field] is None or profile[field] == ""


def evaluate_scheme(profile: dict[str, Any], scheme: dict[str, Any]) -> dict[str, Any]:
    passed, failed, missing = [], [], []
    friendly = {
        "annual_income": "annual family income",
        "project_cost": "project cost",
        "purpose": "purpose",
        "social_category": "social category",
        "caste_certificate": "caste certificate availability",
        "age": "age",
    }
    for field in REQUIRED_FIELDS:
        if _missing(profile, field):
            missing.append(friendly[field])
    if missing:
        return _result(scheme, "UNKNOWN", [], [], missing)

    purpose = str(profile["purpose"]).lower()
    if purpose == scheme["purpose"]:
        passed.append(f"Purpose requirement satisfied: {scheme['purpose'].title()}.")
    else:
        failed.append(f"This scheme is for {scheme['purpose']} requirements, not {purpose}.")

    income = float(profile["annual_income"])
    if income <= scheme["max_income"]:
        passed.append(f"Annual family income is within the indicative limit of Rs. {scheme['max_income']:,}.")
    else:
        failed.append(f"Annual family income exceeds the indicative limit of Rs. {scheme['max_income']:,}.")

    category = str(profile["social_category"]).upper()
    if category in scheme["allowed_categories"]:
        passed.append(f"{category} category requirement satisfied.")
    else:
        failed.append(f"Social category must be one of {', '.join(scheme['allowed_categories'])} for this MVP rule set.")

    if bool(profile["caste_certificate"]):
        passed.append("Caste certificate availability requirement satisfied.")
    else:
        failed.append("A caste certificate is required for this indicative scheme route.")

    project_cost = float(profile["project_cost"])
    if scheme["min_project_amount"] <= project_cost <= scheme["max_project_amount"]:
        passed.append(f"Project amount falls within the Rs. {scheme['min_project_amount']:,} to Rs. {scheme['max_project_amount']:,} range.")
    else:
        failed.append(f"Project cost must be between Rs. {scheme['min_project_amount']:,} and Rs. {scheme['max_project_amount']:,}.")

    return _result(scheme, "ELIGIBLE" if not failed else "NOT_ELIGIBLE", passed, failed, [])


def _result(scheme, status, passed, failed, missing):
    params = {key: scheme[key] for key in ("maximum_loan_amount", "interest_rate", "repayment_years", "moratorium_months")}
    return {
        "scheme_id": scheme["scheme_id"], "scheme_name": scheme["name"], "status": status,
        "reasons": passed if status == "ELIGIBLE" else (failed if status == "NOT_ELIGIBLE" else [f"Eligibility cannot be determined because {', '.join(missing)} was not provided."]),
        "passed_rules": passed, "failed_rules": failed, "missing_fields": missing,
        "financial_parameters": params,
    }


def evaluate_all(profile: dict[str, Any]) -> list[dict[str, Any]]:
    return [evaluate_scheme(profile, scheme) for scheme in SCHEMES]
