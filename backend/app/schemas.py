from typing import Literal
from pydantic import BaseModel, Field, field_validator


class Profile(BaseModel):
    age: int | None = Field(default=None, ge=18, le=100)
    state: str | None = None
    district: str | None = None
    social_category: str | None = None
    annual_income: float | None = Field(default=None, ge=0)
    caste_certificate: bool | None = None
    purpose: Literal["business", "education"] | None = None
    required_amount: float | None = Field(default=None, ge=0)
    project_cost: float | None = Field(default=None, ge=0)
    business_type: str | None = None
    business_stage: str | None = None
    course_type: str | None = None
    course_fee: float | None = Field(default=None, ge=0)
    institution_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class FinanceRequest(BaseModel):
    loan_amount: float = Field(gt=0)
    annual_interest_rate: float = Field(ge=0, le=50)
    repayment_years: int = Field(gt=0, le=30)
    moratorium_months: int = Field(default=0, ge=0, le=120)


class NearbyRequest(BaseModel):
    scheme_id: str
    latitude: float | None = None
    longitude: float | None = None
    state: str | None = None
    district: str | None = None


class ExplainRequest(BaseModel):
    result: dict
