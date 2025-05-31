"""
Configuration settings for the application.
Uses Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from urllib.parse import urlparse, parse_qs


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Database configuration - Updated with Neon support
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/romanian_admin_dev"
    DB_LINK: Optional[str] = None  # For Neon or other external database connections
    
    # Security settings
    SECRET_KEY: str = "dev-secret-key-change-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File upload settings
    UPLOAD_DIRECTORY: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_FILE_TYPES: List[str] = ["pdf", "doc", "docx", "jpg", "jpeg", "png"]
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://127.0.0.1:8080"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Application settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SKIP_DB_INIT: bool = False  # New setting to skip database init in dev
    
    # Email notification settings
    SMTP_SERVER: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@admin.gov.ro"
    FROM_NAME: str = "Platforma Administratiei Publice"
    
    # Frontend URL for email links
    FRONTEND_URL: str = "http://localhost:3000"
    
    @property
    def database_url(self) -> str:
        """
        Get the database URL, preferring DB_LINK if set, converting postgres:// to postgresql+asyncpg:// 
        and handling SSL parameters for Neon compatibility
        """
        # Use DB_LINK if provided, otherwise fall back to DATABASE_URL
        db_url = self.DB_LINK if self.DB_LINK else self.DATABASE_URL
        
        # Convert postgres:// to postgresql+asyncpg://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # For asyncpg, we don't want sslmode=require in the URL
        # SSL will be handled in connect_args
        if "sslmode=require" in db_url:
            db_url = db_url.replace("?sslmode=require", "")
            db_url = db_url.replace("&sslmode=require", "")
        
        return db_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra environment variables


# Global settings instance
settings = Settings() 