from app.rules.rule_engine import evaluate_all
from app.services.finance import calculate_finance
from app.services.location import haversine_km, partner_sort_key
from app.main import explain
from app.schemas import ExplainRequest


def profile(**updates):
    data = {"age": 30, "purpose": "business", "annual_income": 250000, "social_category": "SC", "caste_certificate": True, "project_cost": 120000}
    data.update(updates)
    return data


def by_id(results, id_): return next(item for item in results if item["scheme_id"] == id_)


def test_micro_finance_eligibility():
    assert by_id(evaluate_all(profile()), "micro_finance")["status"] == "ELIGIBLE"


def test_term_loan_eligibility():
    assert by_id(evaluate_all(profile(project_cost=2000000)), "term_loan")["status"] == "ELIGIBLE"


def test_education_eligibility():
    result = by_id(evaluate_all(profile(purpose="education", project_cost=600000)), "education_loan")
    assert result["status"] == "ELIGIBLE"


def test_failed_rule():
    result = by_id(evaluate_all(profile(annual_income=900000)), "micro_finance")
    assert result["status"] == "NOT_ELIGIBLE" and result["failed_rules"]


def test_missing_information_is_unknown():
    assert by_id(evaluate_all(profile(annual_income=None)), "micro_finance")["status"] == "UNKNOWN"


def test_emi_calculation():
    result = calculate_finance(100000, 6.5, 3, 3)
    assert result["monthly_emi"] > 0 and result["total_interest"] > 0


def test_distance():
    assert 0 < haversine_km(12.9716, 77.5946, 19.0760, 72.8777) < 1000


def test_partner_sorting_preserves_zero_distance():
    partners = [{"distance_km": 290.17}, {"distance_km": 0}, {"distance_km": None}]
    assert sorted(partners, key=partner_sort_key)[0]["distance_km"] == 0


def test_missing_gemini_key_returns_rule_result_fallback(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    result = {"scheme_name": "Term Loan", "status": "ELIGIBLE", "passed_rules": ["Income check passed."], "failed_rules": [], "missing_fields": []}

    response = explain(ExplainRequest(result=result))

    assert response["available"] is False
    assert response["source"] == "deterministic fallback"
    assert "marked Term Loan ELIGIBLE" in response["explanation"]
    assert "Income check passed." in response["explanation"]


def test_gemini_timeout_returns_rule_result_fallback(monkeypatch):
    from google import genai

    class TimedOutModels:
        def generate_content(self, **_):
            raise TimeoutError("request timed out")

    class TimedOutClient:
        def __init__(self, **_):
            self.models = TimedOutModels()

    monkeypatch.setattr(genai, "Client", TimedOutClient)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    result = {"scheme_name": "Term Loan", "status": "UNKNOWN", "passed_rules": [], "failed_rules": [], "missing_fields": ["annual family income"]}

    response = explain(ExplainRequest(result=result))

    assert response["available"] is False
    assert response["source"] == "deterministic fallback"
    assert response["error_code"] == "NETWORK_ERROR"
    assert "marked Term Loan UNKNOWN" in response["explanation"]
