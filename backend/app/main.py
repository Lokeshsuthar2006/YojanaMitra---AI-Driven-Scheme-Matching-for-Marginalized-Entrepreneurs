import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DemoProfile, Partner, Scheme
from app.rules.rule_engine import evaluate_all
from app.schemas import ExplainRequest, FinanceRequest, NearbyRequest, Profile
from seed import seed_database
from app.services.finance import calculate_finance
from app.services.location import haversine_km, partner_sort_key

logger = logging.getLogger(__name__)
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
# Existing process-level configuration takes precedence over the optional local file.
load_dotenv(ENV_FILE, override=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_database()
    yield


app = FastAPI(title="ArthSetu API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "ArthSetu deterministic services are available."}


@app.get("/api/schemes")
def schemes(db: Session = Depends(get_db)):
    return [{"scheme_id": item.id, "name": item.name, "purpose": item.purpose, "financial_parameters": item.parameters} for item in db.query(Scheme).all()]


@app.post("/api/eligibility/check")
def eligibility_check(profile: Profile):
    results = evaluate_all(profile.model_dump())
    # Education lending is capped at 90% of course fee or Rs. 40 lakh.
    for item in results:
        if item["scheme_id"] == "education_loan" and profile.course_fee:
            item["financial_parameters"]["maximum_loan_amount"] = min(4000000, profile.course_fee * .9)
    return {"results": results, "principle": "AI interprets. Rules decide. Data routes."}


@app.post("/api/finance/calculate")
def finance(request: FinanceRequest):
    try:
        return calculate_finance(request.loan_amount, request.annual_interest_rate, request.repayment_years, request.moratorium_months)
    except ValueError as error:
        raise HTTPException(422, str(error))


@app.get("/api/partners")
def partners(db: Session = Depends(get_db)):
    return [_partner_dict(item) for item in db.query(Partner).all()]


@app.post("/api/partners/nearby")
def nearby(request: NearbyRequest, db: Session = Depends(get_db)):
    candidates = db.query(Partner).filter(Partner.supported_scheme == request.scheme_id).all()
    routed = []
    for item in candidates:
        record = _partner_dict(item)
        if request.latitude is not None and request.longitude is not None:
            record["distance_km"] = haversine_km(request.latitude, request.longitude, item.latitude, item.longitude)
        else:
            record["distance_km"] = None
            record["local_match"] = item.state == request.state or item.district == request.district
        routed.append(record)
    routed.sort(key=partner_sort_key)
    return {"partners": routed, "disclaimer": "Demo partner data - not live government availability."}


@app.get("/api/demo/profiles")
def demo_profiles(db: Session = Depends(get_db)):
    return [{"id": row.id, "title": row.title, "description": row.description, "profile": row.profile} for row in db.query(DemoProfile).all()]


@app.post("/api/ai/explain")
def explain(request: ExplainRequest):
    result = request.result
    fallback = _rule_explanation(result)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"explanation": fallback, "source": "deterministic fallback", "available": False,
                "error_code": "MISSING_API_KEY", "notice": "Gemini is not configured. Your rule-based result is still available."}
    try:
        from google import genai
        from google.genai import types
        instruction = """You are an explanation assistant for ArthSetu. You do not determine financial or scheme eligibility. Eligibility has already been calculated by a deterministic rule engine. Never change, override, reinterpret, or invent eligibility results. Only explain the supplied output. If missing fields exist say eligibility cannot be determined. Never guarantee loan approval. Financial estimates are indicative only. Use simple language."""
        # The local environment has proxy variables that reject Gemini traffic.
        # Keep this override scoped to the provider client rather than altering global settings.
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=10_000, client_args={"trust_env": False}),
        )
        response = client.models.generate_content(model="gemini-2.5-flash", contents=f"{instruction}\n\nRule engine output: {result}")
        if not isinstance(response.text, str) or not response.text.strip():
            return {"explanation": fallback, "source": "deterministic fallback", "available": False,
                    "error_code": "EMPTY_GEMINI_RESPONSE", "notice": "Gemini returned no explanation. Your rule-based result is still available."}
        return {"explanation": response.text.strip(), "source": "Gemini explanation layer", "available": True}
    except Exception as error:
        error_code, notice = _classify_gemini_error(error)
        logger.warning("Gemini explanation unavailable: %s", error_code)
        return {"explanation": fallback, "source": "deterministic fallback", "available": False,
                "error_code": error_code, "notice": notice}


def _partner_dict(item: Partner):
    return {"partner_id": item.id, "name": item.name, "type": item.type, "supported_scheme": item.supported_scheme, "state": item.state, "district": item.district, "latitude": item.latitude, "longitude": item.longitude, "demo_status": item.demo_status}


def _rule_explanation(result: dict) -> str:
    name, status = result.get("scheme_name", "this scheme"), result.get("status", "UNKNOWN")
    passed = result.get("passed_rules", [])
    failed = result.get("failed_rules", [])
    missing = result.get("missing_fields", [])
    prefix = "This explanation is generated from the deterministic rule-engine results. "
    if status == "ELIGIBLE":
        details = " ".join(passed) or "All configured eligibility conditions were satisfied."
        return f"{prefix}The rule engine marked {name} ELIGIBLE. {details} This is decision support, not a loan approval."
    if status == "UNKNOWN":
        return f"{prefix}The rule engine marked {name} UNKNOWN because required information is missing: {', '.join(missing) or 'additional profile details'}."
    details = " ".join(failed) or "The configured requirements were not satisfied."
    return f"{prefix}The rule engine marked {name} NOT ELIGIBLE under the current MVP rules. Failed checks: {details}"


def _classify_gemini_error(error: Exception) -> tuple[str, str]:
    """Classify provider failures without exposing API keys or raw provider messages."""
    status = getattr(error, "code", None) or getattr(error, "status_code", None)
    message = str(error).lower()
    if status in (401, 403) or "api key" in message or "permission denied" in message:
        return "INVALID_API_KEY", "Gemini could not authenticate the configured API key. Your rule-based result is still available."
    if status == 404 or "model" in message and ("not found" in message or "unsupported" in message):
        return "MODEL_UNAVAILABLE", "The configured Gemini model is unavailable for this project. Your rule-based result is still available."
    if status == 429 or "quota" in message or "resource exhausted" in message:
        return "QUOTA_EXCEEDED", "Gemini's free-tier quota is currently unavailable. Your rule-based result is still available."
    if "connect" in message or "timeout" in message or "timed out" in message or "network" in message or "dns" in message:
        return "NETWORK_ERROR", "ArthSetu could not reach Gemini. Your rule-based result is still available."
    if "google.genai" in message or "genai" in message or "import" in message:
        return "SDK_ERROR", "The Gemini SDK could not complete the explanation request. Your rule-based result is still available."
    return "GEMINI_REQUEST_FAILED", "Gemini explanation is temporarily unavailable. Your rule-based result is still available."
