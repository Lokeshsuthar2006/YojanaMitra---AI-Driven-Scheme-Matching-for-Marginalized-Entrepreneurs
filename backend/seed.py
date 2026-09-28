from app.database import Base, SessionLocal, engine
from app.models import DemoProfile, EligibilityRule, Partner, Scheme
from app.rules.scheme_rules import SCHEMES

PARTNER_CENTERS = [
    ("Delhi", "New Delhi", 28.6139, 77.2090), ("Maharashtra", "Mumbai", 19.0760, 72.8777),
    ("Karnataka", "Bengaluru", 12.9716, 77.5946), ("Tamil Nadu", "Chennai", 13.0827, 80.2707),
    ("West Bengal", "Kolkata", 22.5726, 88.3639), ("Uttar Pradesh", "Lucknow", 26.8467, 80.9462),
    ("Telangana", "Hyderabad", 17.3850, 78.4867), ("Rajasthan", "Jaipur", 26.9124, 75.7873),
]
TYPES = ["SCA", "PSB", "RRB", "NBFC-MFI"]
DEMOS = [
    ("demo_micro", "Micro Finance Match", "A valid small-business profile in Bengaluru.", {"age": 29, "state": "Karnataka", "district": "Bengaluru", "social_category": "SC", "annual_income": 240000, "caste_certificate": True, "purpose": "business", "required_amount": 100000, "project_cost": 120000, "business_type": "Tailoring", "business_stage": "new", "latitude": 12.9716, "longitude": 77.5946}),
    ("demo_term", "Term Loan Match", "A larger manufacturing project in Mumbai.", {"age": 38, "state": "Maharashtra", "district": "Mumbai", "social_category": "OBC", "annual_income": 550000, "caste_certificate": True, "purpose": "business", "required_amount": 1800000, "project_cost": 2200000, "business_type": "Food processing", "business_stage": "existing", "latitude": 19.0760, "longitude": 72.8777}),
    ("demo_education", "Education Loan", "An undergraduate course funding request in Delhi.", {"age": 21, "state": "Delhi", "district": "New Delhi", "social_category": "ST", "annual_income": 360000, "caste_certificate": True, "purpose": "education", "required_amount": 720000, "project_cost": 800000, "course_type": "Engineering", "course_fee": 800000, "institution_type": "Recognised university", "latitude": 28.6139, "longitude": 77.2090}),
    ("demo_failure", "Rule Failure", "A profile that exceeds the income and project rules.", {"age": 42, "state": "Tamil Nadu", "district": "Chennai", "social_category": "General", "annual_income": 1200000, "caste_certificate": False, "purpose": "business", "required_amount": 8000000, "project_cost": 8000000, "business_type": "Logistics", "business_stage": "existing", "latitude": 13.0827, "longitude": 80.2707}),
    ("demo_missing", "Missing Information", "A profile missing income so the engine returns UNKNOWN.", {"age": 30, "state": "West Bengal", "district": "Kolkata", "social_category": "SC", "caste_certificate": True, "purpose": "business", "required_amount": 80000, "project_cost": 100000, "business_type": "Retail", "business_stage": "new", "latitude": 22.5726, "longitude": 88.3639}),
    ("demo_routing", "Nearby Partner Routing", "A routing-focused micro-finance case in Hyderabad.", {"age": 33, "state": "Telangana", "district": "Hyderabad", "social_category": "OBC", "annual_income": 280000, "caste_certificate": True, "purpose": "business", "required_amount": 110000, "project_cost": 130000, "business_type": "Mobile repairs", "business_stage": "existing", "latitude": 17.3850, "longitude": 78.4867}),
]


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Scheme).count(): return
        for scheme in SCHEMES:
            db.add(Scheme(id=scheme["scheme_id"], name=scheme["name"], purpose=scheme["purpose"], parameters=scheme))
            for key in ("purpose", "max_income", "allowed_categories", "max_project_amount"):
                db.add(EligibilityRule(scheme_id=scheme["scheme_id"], rule_key=key, description=f"Deterministic {key} check"))
        for index, (state, district, lat, lon) in enumerate(PARTNER_CENTERS):
            for offset, scheme in enumerate(SCHEMES):
                db.add(Partner(id=f"partner_{index}_{offset}", name=f"ArthSetu Demo {TYPES[(index + offset) % 4]} {district}", type=TYPES[(index + offset) % 4], supported_scheme=scheme["scheme_id"], state=state, district=district, latitude=lat + offset * .018, longitude=lon + offset * .018, demo_status="DEMO DATA"))
        for id_, title, description, profile in DEMOS:
            db.add(DemoProfile(id=id_, title=title, description=description, profile=profile))
        db.commit()
    finally:
        db.close()


if __name__ == "__main__": seed_database()
