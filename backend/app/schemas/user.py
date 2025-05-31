"""
Pydantic schemas for user-related requests and responses.
Provides type-safe validation for user endpoints.
"""

from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from uuid import UUID


class UserRole(str, Enum):
    """User role enumeration"""
    CITIZEN = "citizen"
    OFFICIAL = "official"


class UserCreate(BaseModel):
    """Schema for user registration"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.CITIZEN
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    cnp: Optional[str] = Field(None, max_length=13)


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    cnp: Optional[str] = Field(None, max_length=13)
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user data responses"""
    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    cnp: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v

    @computed_field
    @property
    def name(self) -> str:
        """Computed field that combines first_name and last_name"""
        return f"{self.first_name} {self.last_name}".strip()

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """Schema for detailed user profile"""
    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
    phone: Optional[str] = None
    address: Optional[str] = None
    cnp: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_string(cls, v):
        """Convert UUID to string"""
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @computed_field
    @property
    def name(self) -> str:
        """Computed field that combines first_name and last_name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    class Config:
        from_attributes = True 