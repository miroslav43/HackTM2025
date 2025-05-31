# Database Setup Guide

## Issues Fixed

### 1. Corrupted .env File
- **Problem**: The `DB_LINK` in `.env` was truncated and had invalid characters (`%` at the end)
- **Solution**: Recreated the `.env` file with the correct Neon database URL

### 2. SSL Configuration Issues
- **Problem**: Improper SSL handling for Neon database connections
- **Solution**: Updated `database.py` to properly handle SSL connections with asyncpg driver

### 3. SQL Execution Error
- **Problem**: Raw SQL queries were not wrapped with `text()` function
- **Solution**: Added proper `sqlalchemy.text()` wrapper for raw SQL queries

## Current Configuration

### Environment Variables (.env)
```
DB_LINK=postgresql://neondb_owner:npg_jyNf0P8MrLJD@ep-jolly-meadow-a213esbq-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-secure
```

### Database Features
- ✅ Neon PostgreSQL cloud database
- ✅ SSL/TLS encryption
- ✅ Connection pooling
- ✅ Async SQLAlchemy with asyncpg driver
- ✅ Automatic table creation
- ✅ Error handling for development mode

## Testing

### Database Connection Test
```bash
python test_db.py
```

### Start Application
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Health Check
```bash
curl http://localhost:8000/api/health
```
Expected response:
```json
{
  "status": "healthy",
  "environment": "development", 
  "database": "connected",
  "version": "1.0.0"
}
```

## Database Tables

The following tables are automatically created:
- `users` - User accounts
- `user_activity` - User activity logs
- `documents` - Document management
- `document_categories` - Document categorization
- `archive_documents` - Archived documents
- `document_analysis` - AI document analysis
- `parking_zones` - Parking zone management
- `user_vehicles` - User vehicle registration
- `parking_sessions` - Parking session tracking
- `chat_messages` - AI chat history
- `system_notifications` - System notifications
- `requests` - User requests
- `auth_tokens` - Authentication tokens
- `user_settings` - User preferences

## Troubleshooting

### Connection Issues
1. Verify the `DB_LINK` in `.env` is correct
2. Check internet connectivity to Neon
3. Ensure SSL is properly configured

### Development Mode
- The application will continue running even if database is unavailable
- Check logs for detailed error messages
- Use `SKIP_DB_INIT=true` to skip database initialization if needed 