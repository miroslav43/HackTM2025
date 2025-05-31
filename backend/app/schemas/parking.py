"""
Parking schemas for zones, vehicles, and session management.
Provides type-safe validation for parking-related endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SessionStatus(str, Enum):
    """Parking session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class LocationRequest(BaseModel):
    """Schema for location data"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: Optional[int] = Field(500, ge=100, le=5000)  # meters


class ParkingZoneResponse(BaseModel):
    """Schema for parking zone response"""
    id: str
    name: str
    latitude: Decimal
    longitude: Decimal
    price_per_hour: Decimal
    max_duration: int
    available: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleCreate(BaseModel):
    """Schema for creating user vehicle"""
    license_plate: str = Field(..., min_length=2, max_length=20)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    is_default: bool = False


class VehicleUpdate(BaseModel):
    """Schema for updating user vehicle"""
    license_plate: Optional[str] = Field(None, min_length=2, max_length=20)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    is_default: Optional[bool] = None


class VehicleResponse(BaseModel):
    """Schema for vehicle response"""
    id: str
    user_id: str
    license_plate: str
    brand: Optional[str] = None
    model: Optional[str] = None
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ParkingSessionCreate(BaseModel):
    """Schema for creating parking session"""
    zone_id: str
    vehicle_id: Optional[str] = None
    license_plate: str = Field(..., min_length=2, max_length=20)
    duration_minutes: int = Field(..., ge=5, le=1440)  # 5 min to 24 hours
    payment_method: Optional[str] = Field(None, max_length=50)


class ParkingSessionResponse(BaseModel):
    """Schema for parking session response"""
    id: str
    user_id: str
    zone_id: str
    vehicle_id: Optional[str] = None
    license_plate: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    total_cost: Optional[Decimal] = None
    status: SessionStatus
    payment_method: Optional[str] = None
    created_at: datetime
    
    # Additional fields for response
    zone_name: Optional[str] = None
    remaining_minutes: Optional[int] = None

    class Config:
        from_attributes = True


class NearbyZonesRequest(BaseModel):
    """Schema for finding nearby parking zones"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: int = Field(500, ge=100, le=5000)  # meters 