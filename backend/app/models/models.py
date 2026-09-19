import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base

class UserRole(str, enum.Enum):
    COLLECTOR = "collector"
    RECYCLER = "recycler"
    ADMIN = "admin"

class ScrapStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    OFFER_ACCEPTED = "offer_accepted"
    COLLECTED = "collected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OfferStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"

class PickupStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    FAILED = "failed"

class RecyclingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    collector_profile = relationship("Collector", back_populates="user", uselist=False)
    recycler_profile = relationship("Recycler", back_populates="user", uselist=False)

class Collector(Base):
    __tablename__ = "collectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    verification_status = Column(Boolean, default=True)

    user = relationship("User", back_populates="collector_profile")
    scrap_items = relationship("ScrapItem", back_populates="collector")
    transactions = relationship("Transaction", back_populates="collector")

class Recycler(Base):
    __tablename__ = "recyclers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(150), nullable=False)
    license_number = Column(String(100), unique=True, nullable=False)
    accepted_materials = Column(ARRAY(String), nullable=False)
    service_area = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    verification_status = Column(Boolean, default=False)
    rating = Column(Float, default=5.0)

    user = relationship("User", back_populates="recycler_profile")
    offers = relationship("Offer", back_populates="recycler")
    transactions = relationship("Transaction", back_populates="recycler")

class ScrapItem(Base):
    __tablename__ = "scrap_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collector_id = Column(UUID(as_uuid=True), ForeignKey("collectors.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    predicted_category = Column(String(50), nullable=True)
    quality = Column(String(50), nullable=False)
    predicted_quality = Column(String(50), nullable=True)
    weight = Column(Float, nullable=False)
    image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ScrapStatus), default=ScrapStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    collector = relationship("Collector", back_populates="scrap_items")
    offers = relationship("Offer", back_populates="scrap_item")
    transaction = relationship("Transaction", back_populates="scrap_item", uselist=False)

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scrap_id = Column(UUID(as_uuid=True), ForeignKey("scrap_items.id", ondelete="CASCADE"), nullable=False)
    recycler_id = Column(UUID(as_uuid=True), ForeignKey("recyclers.id", ondelete="CASCADE"), nullable=False)
    offered_price = Column(Float, nullable=False)
    pickup_available = Column(Boolean, default=True)
    estimated_pickup_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(OfferStatus), default=OfferStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    scrap_item = relationship("ScrapItem", back_populates="offers")
    recycler = relationship("Recycler", back_populates="offers")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scrap_id = Column(UUID(as_uuid=True), ForeignKey("scrap_items.id", ondelete="CASCADE"), nullable=False)
    collector_id = Column(UUID(as_uuid=True), ForeignKey("collectors.id", ondelete="CASCADE"), nullable=False)
    recycler_id = Column(UUID(as_uuid=True), ForeignKey("recyclers.id", ondelete="CASCADE"), nullable=False)
    accepted_price = Column(Float, nullable=False)
    pickup_status = Column(SQLEnum(PickupStatus), default=PickupStatus.SCHEDULED)
    recycling_status = Column(SQLEnum(RecyclingStatus), default=RecyclingStatus.PENDING)
    transaction_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    scrap_item = relationship("ScrapItem", back_populates="transaction")
    collector = relationship("Collector", back_populates="transactions")
    recycler = relationship("Recycler", back_populates="transactions")
    recycling_record = relationship("RecyclingRecord", back_populates="transaction", uselist=False)

class RecyclingRecord(Base):
    __tablename__ = "recycling_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), unique=True, nullable=False)
    material_type = Column(String(50), nullable=False)
    weight = Column(Float, nullable=False)
    recycling_method = Column(String(100), nullable=False)
    completion_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    certificate_reference_number = Column(String(100), unique=True, nullable=False)

    transaction = relationship("Transaction", back_populates="recycling_record")
