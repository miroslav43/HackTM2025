# Romanian Public Administration Backend

A complete FastAPI backend for the Romanian public administration document management platform. Built with modern async Python, PostgreSQL, and comprehensive security features.

## 🏗️ Architecture

### Tech Stack
- **FastAPI 0.104.1** - Modern, fast web framework with automatic API documentation
- **PostgreSQL** - Robust relational database with async support via Neon
- **SQLAlchemy 2.0** - Modern ORM with async capabilities
- **Pydantic v2** - Data validation and serialization
- **JWT + bcrypt** - Secure authentication and password hashing
- **aiofiles + Pillow** - Async file handling and image processing

### Project Structure
```
backend/
├── app/
│   ├── api/routes/          # API endpoint definitions
│   │   ├── auth.py          # Authentication & registration
│   │   ├── documents.py     # Document management
│   │   ├── archive.py       # Public document archive
│   │   ├── dashboard.py     # Statistics & notifications
│   │   ├── users.py         # User management
│   │   ├── settings.py      # User preferences & config
│   │   ├── ai.py           # AI agent integration
│   │   └── parking.py       # Parking system (placeholder)
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings & environment
│   │   ├── security.py     # JWT & password handling
│   │   └── dependencies.py # Auth middleware
│   ├── db/                 # Database configuration
│   │   └── database.py     # Async SQLAlchemy setup
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── user.py         # Users & activities
│   │   ├── document.py     # Documents & archive
│   │   ├── notification.py # Notifications
│   │   ├── auth_token.py   # Session management
│   │   ├── settings.py     # User settings
│   │   └── parking.py      # Parking system
│   ├── schemas/            # Pydantic validation schemas
│   │   ├── user.py         # User data validation
│   │   ├── document.py     # Document schemas
│   │   ├── dashboard.py    # Dashboard & notifications
│   │   ├── parking.py      # Parking schemas
│   │   └── common.py       # Shared schemas
│   ├── services/           # Business logic layer
│   │   ├── user_service.py          # User authentication
│   │   ├── document_service.py      # Document operations
│   │   ├── dashboard_service.py     # Statistics & notifications
│   │   ├── user_management_service.py # User administration
│   │   └── settings_service.py      # Settings management
│   └── utils/              # Utility functions
│       └── file_handler.py # File upload & validation
├── main.py                 # FastAPI app & route registration
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database (Neon recommended)
- Git

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**:
Create `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
UPLOAD_DIRECTORY=uploads
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=pdf,doc,docx,jpg,jpeg,png

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CORS_CREDENTIALS=true
CORS_METHODS=["*"]
CORS_HEADERS=["*"]

# Environment
ENVIRONMENT=development
DEBUG=true
```

3. **Run the application**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `POST /logout` - User logout
- `GET /me` - Get current user profile
- `PUT /me` - Update current user profile

### Document Management (`/api/documents`)
- `POST /upload` - Upload document for verification
- `GET /` - List user documents (paginated)
- `GET /{id}` - Get document details
- `GET /{id}/download` - Download document file
- `PUT /{id}/verify` - Verify/reject document (officials only)
- `DELETE /{id}` - Delete document
- `GET /pending/verification` - Get pending verifications (officials)
- `GET /stats/summary` - Get document statistics

### Public Archive (`/api/archive`)
- `GET /search` - Search public documents (advanced filters)
- `GET /categories` - List document categories
- `POST /categories` - Create category (officials only)
- `GET /categories/{id}/documents` - Documents by category
- `GET /documents/{id}` - Get archive document details
- `GET /documents/{id}/download` - Download archive document
- `POST /documents` - Add document to archive (officials only)
- `GET /stats` - Archive statistics

### Dashboard (`/api/dashboard`)
- `GET /stats` - Dashboard statistics
- `POST /activity/log` - Log user activity
- `GET /activity` - Get user activities
- `GET /activity/system` - Get system activities (officials)
- `GET /analytics` - Activity analytics for charts
- `GET /notifications` - Get user notifications
- `GET /notifications/count` - Get notification counts
- `POST /notifications` - Create notification (officials)
- `PUT /notifications/{id}/read` - Mark notification as read
- `PUT /notifications/read-all` - Mark all notifications as read
- `DELETE /notifications/{id}` - Delete notification

### User Management (`/api/users`)

#### Profile Management
- `GET /profile` - Get current user profile
- `PUT /profile` - Update user profile
- `POST /profile/avatar` - Upload user avatar
- `GET /profile/avatar` - Get user avatar
- `PUT /profile/password` - Change password
- `DELETE /profile` - Deactivate account

#### Session Management
- `GET /sessions` - Get active sessions
- `DELETE /sessions/{id}` - Revoke specific session
- `DELETE /sessions` - Revoke all sessions

#### Admin Functions (Officials Only)
- `GET /` - List all users with filtering
- `GET /{id}` - Get user by ID
- `POST /` - Create user by admin
- `PUT /{id}/role` - Update user role
- `PUT /{id}/deactivate` - Deactivate user
- `PUT /{id}/reactivate` - Reactivate user
- `DELETE /{id}` - Delete user permanently
- `GET /{id}/statistics` - Get user statistics

### Settings (`/api/settings`)

#### General Settings
- `GET /` - Get all user settings
- `GET /{key}` - Get specific setting
- `PUT /` - Set/update setting
- `PUT /bulk` - Set multiple settings
- `DELETE /{key}` - Delete setting
- `DELETE /` - Delete all settings

#### Specialized Settings
- `GET /notifications` - Get notification settings
- `PUT /notifications` - Update notification settings
- `GET /privacy` - Get privacy settings
- `PUT /privacy` - Update privacy settings
- `GET /ui` - Get UI preferences
- `PUT /ui` - Update UI preferences
- `GET /security` - Get security settings
- `PUT /security` - Update security settings

#### System & Data
- `GET /system` - Get system settings (officials only)
- `GET /export` - Export user settings
- `POST /import` - Import user settings

### AI Agent (`/api/ai`)
- `POST /chat` - Chat with AI assistant
- `GET /chat/history` - Get chat history
- `DELETE /chat/history` - Clear chat history

## 🔐 Security Features

### Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (citizen vs official permissions)
- **Password hashing** using bcrypt with salt
- **Session management** with token revocation
- **Input validation** via Pydantic schemas

### File Security
- **File type validation** (MIME type + extension checking)
- **File size limits** (configurable)
- **Path traversal protection**
- **Secure file storage** with unique naming
- **Image optimization** for avatars

### Data Protection
- **SQL injection prevention** via SQLAlchemy ORM
- **XSS protection** through input sanitization
- **CORS configuration** for frontend integration
- **Environment-based configuration**

## 💾 Database Schema

### Core Tables
- **Users** - Authentication, profiles, roles
- **Documents** - User-uploaded documents with verification
- **ArchiveDocuments** - Public document repository
- **DocumentCategories** - Document categorization
- **UserActivity** - Activity logging and tracking
- **Notifications** - User notifications system
- **AuthTokens** - Session management
- **UserSettings** - User preferences (key-value store)

### Relationships
- Users → Documents (one-to-many)
- Users → Notifications (one-to-many)
- Users → UserActivity (one-to-many)
- Users → AuthTokens (one-to-many)
- Users → UserSettings (one-to-many)
- DocumentCategories → ArchiveDocuments (one-to-many)

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `UPLOAD_DIRECTORY` | File upload directory | `uploads` |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `52428800` (50MB) |
| `ALLOWED_FILE_TYPES` | Comma-separated file extensions | `pdf,doc,docx,jpg,jpeg,png` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |
| `ENVIRONMENT` | Runtime environment | `development` |
| `DEBUG` | Enable debug mode | `false` |

### File Upload Settings
- **Maximum file size**: 50MB (configurable)
- **Allowed types**: PDF, DOC, DOCX, JPG, JPEG, PNG
- **Storage**: Local filesystem with organized subdirectories
- **Processing**: Automatic image optimization for avatars

## 🧪 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Database Migrations
The application uses SQLAlchemy models with automatic table creation. For production, consider using Alembic for migrations:

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Code Quality
```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
1. **Database**: Use production PostgreSQL instance
2. **File Storage**: Consider cloud storage (AWS S3, etc.)
3. **Secrets**: Use environment-specific secret management
4. **Monitoring**: Add logging and monitoring tools
5. **Security**: Enable HTTPS, set secure CORS origins

### Performance Optimization
- **Database connection pooling**
- **File upload streaming**
- **Caching for frequent queries**
- **Background task processing**
- **CDN for static files**

## 📖 API Usage Examples

### Authentication Flow
```python
# Register user
response = requests.post("http://localhost:8000/api/auth/register", json={
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
})

# Login
response = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "secure_password"
})
token = response.json()["access_token"]

# Use token for authenticated requests
headers = {"Authorization": f"Bearer {token}"}
```

### Document Upload
```python
# Upload document
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "name": "My Document",
        "type": "other",
        "description": "Important document"
    }
    response = requests.post(
        "http://localhost:8000/api/documents/upload",
        headers=headers,
        files=files,
        data=data
    )
```

### Archive Search
```python
# Search archive documents
response = requests.get(
    "http://localhost:8000/api/archive/search",
    params={
        "q": "search term",
        "category_id": "uuid-here",
        "page": 1,
        "limit": 20
    }
)
documents = response.json()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Format code (`black` and `isort`)
7. Submit a pull request

## 📄 License

This project is part of a Romanian public administration platform. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/api/docs`
2. Review the code examples above
3. Check existing GitHub issues
4. Create a new issue with detailed information

---

**Built with ❤️ for Romanian Public Administration** 