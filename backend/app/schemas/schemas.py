from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.models import UserRole, ScrapStatus, OfferStatus, PickupStatus, RecyclingStatus

# Auth Schemas
class UserRegister(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    role: UserRole
    location: Optional[str] = "Chennai"

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    user_id: UUID

class UserOut(BaseModel):
    id: UUID
    name: str
    phone: str
    email: Optional[str]
    role: UserRole
    location: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Collector Profile
class CollectorOut(BaseModel):
    id: UUID
    user_id: UUID
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    verification_status: bool
    user: UserOut

    class Config:
        from_attributes = True

# Recycler Profile
class RecyclerCreate(BaseModel):
    company_name: str
    license_number: str
    accepted_materials: List[str]
    service_area: str
    latitude: float
    longitude: float

class RecyclerOut(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    license_number: str
    accepted_materials: List[str]
    service_area: str
    latitude: float
    longitude: float
    verification_status: bool
    rating: float
    user: UserOut

    class Config:
        from_attributes = True

# Scrap Schemas
class ScrapCreate(BaseModel):
    category: str
    quality: str
    weight: float
    description: Optional[str] = None

class ScrapOut(BaseModel):
    id: UUID
    collector_id: UUID
    category: str
    predicted_category: Optional[str]
    quality: str
    predicted_quality: Optional[str]
    weight: float
    image_url: Optional[str]
    description: Optional[str]
    status: ScrapStatus
    created_at: datetime

    class Config:
        from_attributes = True

# Offer Schemas
class OfferCreate(BaseModel):
    scrap_id: UUID
    offered_price: float
    estimated_pickup_date: Optional[datetime] = None

class OfferOut(BaseModel):
    id: UUID
    scrap_id: UUID
    recycler_id: UUID
    offered_price: float
    pickup_available: bool
    estimated_pickup_date: Optional[datetime]
    status: OfferStatus
    created_at: datetime
    recycler: Optional[RecyclerOut] = None

    class Config:
        from_attributes = True

# Transaction & Tracking Schemas
class TransactionOut(BaseModel):
    id: UUID
    scrap_id: UUID
    collector_id: UUID
    recycler_id: UUID
    accepted_price: float
    pickup_status: PickupStatus
    recycling_status: RecyclingStatus
    transaction_date: datetime
    completed_at: Optional[datetime]
    scrap_item: Optional[ScrapOut] = None
    recycler: Optional[RecyclerOut] = None

    class Config:
        from_attributes = True

# Matching Schemas
class FactorBreakdown(BaseModel):
    material_match: float
    distance_score: float
    price_score: float
    verification_score: float
    availability_score: float
    rating_score: float

class RecommendationResult(BaseModel):
    recycler: RecyclerOut
    match_score: float
    breakdown: FactorBreakdown
    explanation: str

# ML Output Schema
class MLClassificationResult(BaseModel):
    category: str
    confidence: float
    quality: str
    quality_confidence: float
    requires_manual_confirmation: bool
