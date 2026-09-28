from sqlalchemy import Boolean, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Demo user")


class Scheme(Base):
    __tablename__ = "schemes"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    purpose: Mapped[str] = mapped_column(String(30))
    parameters: Mapped[dict] = mapped_column(JSON)


class Partner(Base):
    __tablename__ = "partners"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(30))
    supported_scheme: Mapped[str] = mapped_column(String(50))
    state: Mapped[str] = mapped_column(String(80))
    district: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    demo_status: Mapped[str] = mapped_column(String(40), default="DEMO DATA")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    scheme_id: Mapped[str] = mapped_column(String(50))
    rule_key: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(300))


class DemoProfile(Base):
    __tablename__ = "demo_profiles"
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(300))
    profile: Mapped[dict] = mapped_column(JSON)
