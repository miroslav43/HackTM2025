"""
Parking models for location-based parking management.
Includes parking zones, user vehicles, and parking sessions.
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text

from ..db.database import Base


class ParkingZone(Base):
    """
    Parking zones with location and pricing information
    """
    __tablename__ = "parking_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String(255), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    price_per_hour = Column(Numeric(8, 2), nullable=False)
    max_duration = Column(Integer, nullable=False)  # în ore
    available = Column(Boolean, server_default="true")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp())


class UserVehicle(Base):
    """
    User registered vehicles
    """
    __tablename__ = "user_vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    license_plate = Column(String(20), nullable=False)
    brand = Column(String(100))
    model = Column(String(100))
    is_default = Column(Boolean, server_default="false")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class ParkingSession(Base):
    """
    Active and completed parking sessions
    """
    __tablename__ = "parking_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("parking_zones.id"))
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("user_vehicles.id"))
    license_plate = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    duration_minutes = Column(Integer)
    total_cost = Column(Numeric(8, 2))
    status = Column(String(20), server_default="active")
    payment_method = Column(String(50))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    
    # Add check constraint for status
    __table_args__ = (
        CheckConstraint("status IN ('active', 'completed', 'expired')", name='parking_sessions_status_check'),
    ) 