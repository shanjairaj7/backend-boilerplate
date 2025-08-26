# Authentication System

This backend boilerplate includes a complete JWT-based authentication system with user management.

## ⚠️ IMPLEMENTATION STATUS

**BACKEND**: ✅ **FULLY IMPLEMENTED** - All authentication routes are working and deployed
**FRONTEND**: ❌ **NOT INTEGRATED** - Frontend authentication pages exist but are NOT connected to backend API

## 🏗️ BACKEND ARCHITECTURE OVERVIEW

### Route Protection Strategy

**DEFAULT CONFIGURATION**: Routes are **NOT protected by default**

- Only routes with `Depends(get_current_user)` require authentication
- New routes can be added as public endpoints without authentication
- Authentication is **OPTIONAL** and route-specific

### Available Authentication Endpoints

| Endpoint        | Method | Protection   | Description       | Request Body                  | Response              |
| --------------- | ------ | ------------ | ----------------- | ----------------------------- | --------------------- |
| `/auth/signup`  | POST   | 🟢 Public    | Register new user | `{username, email, password}` | JWT token + user data |
| `/auth/login`   | POST   | 🟢 Public    | User login        | `{username, password}`        | JWT token + user data |
| `/auth/profile` | GET    | 🔒 Protected | Get user profile  | None                          | User data             |
| `/auth/logout`  | POST   | 🔒 Protected | Logout user       | None                          | Success message       |

### Authentication Response Format

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

### JWT Token Configuration

- **Algorithm**: HS256
- **Expiration**: 30 minutes (1800 seconds)
- **Header**: `Authorization: Bearer <token>`
- **Payload**: `{"sub": "user_id", "username": "username", "exp": timestamp}`

## Features

- **User Registration** (`POST /auth/signup`)
- **User Login** (`POST /auth/login`)
- **Profile Management** (`GET/PUT /auth/profile`)
- **Password Change** (`POST /auth/change-password`)
- **Token Refresh** (`POST /auth/refresh-token`)
- **JWT Token-based Authentication**
- **Password Hashing** (bcrypt)
- **SQLAlchemy Database Integration**

## API Endpoints

### Public Endpoints

| Method | Endpoint       | Description                  |
| ------ | -------------- | ---------------------------- |
| POST   | `/auth/signup` | Register a new user          |
| POST   | `/auth/login`  | Login with username/password |

### Protected Endpoints (Require Bearer Token)

| Method | Endpoint                | Description              |
| ------ | ----------------------- | ------------------------ |
| GET    | `/auth/profile`         | Get current user profile |
| PUT    | `/auth/profile`         | Update user profile      |
| POST   | `/auth/change-password` | Change user password     |
| POST   | `/auth/refresh-token`   | Refresh access token     |

## Usage Examples

### 1. User Registration

```bash
curl -X POST "{DEPLOYED_BACKEND_URL}/auth/signup" \
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
curl -X POST "{DEPLOYED_BACKEND_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### 3. Access Protected Endpoint

```bash
curl -X GET "{DEPLOYED_BACKEND_URL}/auth/profile" \
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

## 🎨 FRONTEND CURRENT STATE

### Current Frontend Architecture

The frontend currently has **dummy authentication** implemented:

**Existing Pages**: ✅ All auth pages exist

- `LoginPage.tsx` - Login form (dummy logic)
- `SignupPage.tsx` - Signup form (dummy logic)
- `ProfilePage.tsx` - User profile display (mock data)
- `protected-route.tsx` - Route protection wrapper

**Current Auth Store** (`src/stores/auth-store.ts`):

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}
```

**Current App.tsx Structure**:

```jsx
<Routes>
  {/* Public routes */}
  <Route path="/login" element={<LoginPage />} />
  <Route path="/signup" element={<SignupPage />} />

  {/* Protected routes - CURRENTLY ACTIVE */}
  <Route
    path="/"
    element={
      <ProtectedRoute>
        <TodoDashboardPage />
      </ProtectedRoute>
    }
  />
  <Route
    path="/settings"
    element={
      <ProtectedRoute>
        <SettingsPage />
      </ProtectedRoute>
    }
  />
  <Route
    path="/profile"
    element={
      <ProtectedRoute>
        <ProfilePage />
      </ProtectedRoute>
    }
  />
</Routes>
```

## 🔄 IMPLEMENTATION DECISION POINT

**YOU must choose ONE of these implementation paths:**

## ⚠️ CRITICAL AUTHENTICATION REQUIREMENT

**If the user requests authentication implementation OR if authentication is necessary for the app functionality:**

**MANDATORY**: YOU MUST implement full authentication integration with the frontend

- This is NOT optional - authentication MUST be fully integrated
- Add authentication implementation as a TODO item using `<action type="todo_create">`
- Follow Option A instructions completely
- Connect all frontend auth pages to real backend APIs
- Implement JWT token management in Zustand store
- Ensure protected routes work with real authentication
- Test the complete authentication flow

**DO NOT choose Option B (skip auth) if the user wants or needs authentication functionality**

---

## 🔐 OPTION A: IMPLEMENT FULL AUTHENTICATION

**When to choose**: Production apps, demos requiring real login functionality

### Step 1: Update Auth API Layer

**CREATE THIS FILE**: `frontend/src/api/auth_api.ts`

Replace dummy logic with real backend calls:

```typescript
const BACKEND_URL = 'https://your-backend-url.modal.run';

export const authAPI = {
  signup: async (userData) => {
    const response = await fetch(`${BACKEND_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return response.json(); // Returns: {access_token, token_type, expires_in, user}
  },

  login: async (credentials) => {
    const response = await fetch(`${BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return response.json(); // Returns: {access_token, token_type, expires_in, user}
  },
};
```

### Step 2: Enhanced Zustand Auth Store

**CREATE THIS FILE**: `frontend/src/stores/auth-store.ts`

Replace existing store with JWT-aware version:

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  signup: (userData: SignupData) => Promise<void>;
  login: (credentials: LoginData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}
```

**Key Requirements**:

- Store JWT token in localStorage/sessionStorage
- Add loading states for async operations
- Handle authentication errors
- Implement automatic token refresh
- Clear tokens on logout

### Step 3: Connect Auth Pages

**UPDATE THESE FILES**: `LoginPage.tsx`, `SignupPage.tsx`

- Connect form submissions to real auth store methods
- Display loading states during API calls
- Show error messages from API responses
- Redirect to dashboard on successful authentication

### Step 4: Enhanced Protected Routes

**UPDATE THESE FIELS**: `components/protected-route.tsx`

- Check for valid, unexpired JWT tokens
- Redirect to login if token is missing/expired
- Implement token refresh logic
- Handle authentication state changes

### Step 5: API Request Authentication

**MAKE THIS UPDATE**
**Pattern**: Add JWT tokens to all authenticated API requests

```typescript
fetch(url, {
  headers: {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});
```

---

## 🚀 OPTION B: SKIP AUTHENTICATION (RAPID PROTOTYPING)

**When to choose**: Quick demos, MVPs, non-user-facing prototypes

### Step 1: Disable Protected Routes

**CREATE THIS FILE**: `App.tsx`

Comment out all `<ProtectedRoute>` wrappers:

```jsx
<Routes>
  {/* Keep login/signup for UI completeness */}
  <Route path="/login" element={<LoginPage />} />
  <Route path="/signup" element={<SignupPage />} />

  {/* Remove ProtectedRoute wrappers - direct access */}
  <Route path="/" element={<TodoDashboardPage />} />
  <Route path="/settings" element={<SettingsPage />} />
  <Route path="/profile" element={<ProfilePage />} />
</Routes>
```

### Step 2: Mock Authentication State

**CREATE THIS FILE**: `src/stores/auth-store.ts`

Set permanent authenticated state:

```typescript
export const useAuthStore = create<AuthState>(() => ({
  user: {
    id: 'demo-user',
    name: 'Demo User',
    email: 'demo@example.com',
  },
  isAuthenticated: true, // Always authenticated
  login: () => {}, // No-op
  logout: () => {}, // No-op
}));
```

### Step 3: Remove Authentication Dependencies

- Remove JWT token logic from API calls
- Skip error handling for authentication failures
- Remove loading states for auth operations
- Allow direct navigation to all pages

### Step 4: Navigation Updates (Optional)

- Hide login/logout buttons from navigation
- Remove user profile management features
- Skip authentication-related UI components

---

## 🎯 DECISION MATRIX

| Requirement             | Option A (Full Auth) | Option B (Skip Auth) |
| ----------------------- | -------------------- | -------------------- |
| **Development Time**    | 2-4 hours            | 30 minutes           |
| **User Management**     | ✅ Real users        | ❌ Demo only         |
| **Security**            | ✅ JWT-based         | ❌ No protection     |
| **Production Ready**    | ✅ Yes               | ❌ No                |
| **Demo Friendly**       | ⚠️ Requires signup   | ✅ Immediate access  |
| **Backend Integration** | ✅ Full integration  | ❌ No backend calls  |

## 🚨 CRITICAL IMPLEMENTATION NOTES

1. **Current State**: Frontend has all auth pages but they're using dummy logic
2. **Protected Routes**: Currently ACTIVE - will block access without real auth
3. **Auth Store**: Currently minimal - needs expansion for real JWT handling
4. **Backend Ready**: All auth endpoints already implemented and tested
5. **Decision Required**: Must choose Option A or B - cannot mix approaches

## 🎯 MANDATORY TODO CREATION

**When implementing authentication (Option A), YOU MUST:**

1. **Create TODO Item**: Use `<action type="todo_create" id="auth_integration" priority="high" integration="true">` to track authentication implementation
2. **Update TODO Progress**: Mark as `in_progress` when starting implementation
3. **Complete TODO**: Mark as `completed` only when full authentication flow is working
4. **Integration Testing**: Ensure signup, login, protected routes, and logout all function correctly

**Example TODO Creation**:

```xml
<action type="todo_create" id="auth_integration" priority="high" integration="true">
Implement full authentication integration: connect frontend auth pages to backend APIs, implement JWT token management in Zustand store, ensure protected routes work with real authentication
</action>
```

## Production Considerations

1. **Use a strong SECRET_KEY** (generate with `openssl rand -base64 32`)
2. **Use PostgreSQL** instead of SQLite for production
3. **Set appropriate token expiration** times
4. **Enable HTTPS** in production
5. **Consider implementing refresh token rotation**
6. **Add rate limiting** for auth endpoints
