# Authentication System

This backend boilerplate includes a complete JWT-based authentication system with user management.

## Features

- **User Registration** (`POST /auth/signup`)
- **User Login** (`POST /auth/login`)
- **Profile Management** (`GET/PUT /auth/profile`)
- **Password Change** (`POST /auth/change-password`)
- **Token Refresh** (`POST /auth/refresh-token`)
- **JWT Token-based Authentication**
- **Password Hashing** (bcrypt)
- **SQLAlchemy Database Integration**

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run the Server**
   ```bash
   python app.py
   ```

4. **Test the Authentication**
   ```bash
   python test_auth_api.py
   ```

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login with username/password |

### Protected Endpoints (Require Bearer Token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/auth/profile` | Get current user profile |
| PUT | `/auth/profile` | Update user profile |
| POST | `/auth/change-password` | Change user password |
| POST | `/auth/refresh-token` | Refresh access token |

## Usage Examples

### 1. User Registration
```bash
curl -X POST "http://localhost:8892/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. User Login
```bash
curl -X POST "http://localhost:8892/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### 3. Access Protected Endpoint
```bash
curl -X GET "http://localhost:8892/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Database Schema

The authentication system uses a `users` table with the following fields:

- `id` (Primary Key)
- `username` (Unique, Required)
- `email` (Unique, Required)
- `hashed_password` (Required)
- `first_name` (Optional)
- `last_name` (Optional)
- `is_active` (Boolean, Default: True)
- `is_verified` (Boolean, Default: False)
- `created_at` (Timestamp)
- `updated_at` (Timestamp)

## Security Features

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Token Validation**: Automatic token verification on protected routes
- **User Status**: Support for active/inactive and verified/unverified users
- **Secure Defaults**: Environment-based configuration with secure fallbacks

## Configuration

Set these environment variables in your `.env` file:

```env
# Required
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db

# Optional (with defaults)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Modular Design

The authentication system is designed to be **optionally integrated**:

- **Standalone**: Can run independently without affecting other APIs
- **Modular**: Easy to include/exclude from projects
- **Configurable**: Optional import in `services/__init__.py`
- **Self-contained**: All auth logic in dedicated files

## File Structure

```
backend-boilerplate/
├── models/
│   └── auth_models.py          # Pydantic models for requests/responses
├── services/
│   └── auth_service.py         # FastAPI routes and endpoint logic
├── utils/
│   └── auth.py                 # JWT and password utilities
├── database/
│   └── user.py                 # SQLAlchemy User model
├── test_auth_api.py            # Complete API test suite
└── AUTH_README.md              # This documentation
```

## Testing

Run the comprehensive test suite:

```bash
python test_auth_api.py
```

The test script will:
- Test user registration and login
- Verify token-based authentication
- Test profile management
- Test password changes
- Verify security (unauthorized access protection)

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created (successful registration)
- `400` - Bad Request (validation errors, duplicate users)
- `401` - Unauthorized (invalid credentials, expired tokens)
- `422` - Unprocessable Entity (validation errors)

## Production Considerations

1. **Use a strong SECRET_KEY** (generate with `openssl rand -base64 32`)
2. **Use PostgreSQL** instead of SQLite for production
3. **Set appropriate token expiration** times
4. **Enable HTTPS** in production
5. **Consider implementing refresh token rotation**
6. **Add rate limiting** for auth endpoints