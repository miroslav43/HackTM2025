"""
Configuration settings for the application.
Uses Pydantic Settings for environment variable management.
"""

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
import os
from urllib.parse import urlparse, parse_qs
from pydantic import Field


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
    
    # AI Agent Configuration
    gemini_key: Optional[str] = Field(None, env="GEMINI_KEY")
    perplexity_api_key: Optional[str] = Field(None, env="PERPLEXITY_API_KEY")
    
    # AI Agent Settings
    ai_agent_enabled: bool = Field(True, env="AI_AGENT_ENABLED")
    ai_agent_timeout: int = Field(120, env="AI_AGENT_TIMEOUT")  # seconds
    ai_agent_max_retries: int = Field(3, env="AI_AGENT_MAX_RETRIES")
    
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
    
    def validate_ai_agent_config(self) -> Dict[str, bool]:
        """Validate AI agent configuration"""
        validation = {
            "gemini_key_set": bool(self.gemini_key),
            "perplexity_key_set": bool(self.perplexity_api_key),
            "agent_enabled": self.ai_agent_enabled
        }
        validation["fully_configured"] = all([
            validation["gemini_key_set"],
            validation["perplexity_key_set"],
            validation["agent_enabled"]
        ])
        return validation
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra environment variables


# Global settings instance
settings = Settings() 