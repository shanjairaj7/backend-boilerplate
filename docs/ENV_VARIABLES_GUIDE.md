# API Keys and Environment Variables Handling Guide

This documentation provides guidance for secure handling of API keys and environment variables.

## 🔐 ENVIRONMENT VARIABLE REQUIREMENTS

### Default Environment State
**By default, no environment variables are available in the backend**
- Fresh deployments have empty environment configuration
- All API keys must be explicitly added by the user
- Never assume any environment variables exist without user configuration

### Key Loading Pattern
**Always load keys from environment variables**:
- Use `os.getenv("KEY_NAME")` to load all API keys
- Check if key exists before using it
- Handle missing keys gracefully with helpful error messages
- Never hardcode API keys in source code

## 🚨 SECURITY REQUIREMENTS

### API Key Visibility
**Never expose API keys in responses**:
- Do not include API keys in JSON responses
- Do not log API keys to console or files
- Do not return keys in error messages or debug information
- Mask keys in any user-facing output

### Error Handling for Missing Keys
When API keys are missing:
- Return helpful error message without exposing key values
- Guide user to add keys through Dashboard → Backend → Secrets
- Do not attempt API calls without proper authentication
- Fail gracefully with clear instructions

## 📚 DOCUMENTATION-FIRST APPROACH

### Check Existing Documentation
**Before implementing any third-party API integration**:
- Check if documentation exists in `backend/docs/` folder
- Read the full documentation if it exists
- Follow the specific key handling instructions for that API
- Use the documented environment variable names and patterns

### Documentation Priority
If documentation exists for a specific API:
- Follow the documented approach exactly
- Use the specified environment variable names
- Implement the documented error handling patterns
- Follow any specific security requirements mentioned

## 🛠️ IMPLEMENTATION PATTERN

### Environment Variable Loading
```python
import os

# Load API key from environment
API_KEY = os.getenv("SERVICE_API_KEY")

# Always check if key exists
if not API_KEY:
    # Handle missing key appropriately
    raise HTTPException(
        status_code=500, 
        detail="SERVICE_API_KEY not configured. Please add it in Dashboard → Backend → Secrets"
    )
```

### Secure Response Handling
**Never return keys in responses**:
- Filter out sensitive data from API responses
- Use response models that exclude sensitive fields
- Mask any key-like strings in error messages

## 🚨 MANDATORY REQUIREMENTS

**Must Do**:
1. **Environment Variables**: All keys from `os.getenv()`, never hardcoded
2. **Check Documentation**: Read existing docs before implementing APIs
3. **Secure Responses**: Never expose API keys in responses or logs
4. **Missing Key Handling**: Graceful error messages with user guidance
5. **Default Empty State**: Assume no environment variables exist initially

**Must Not Do**:
- Never hardcode API keys in source code
- Never return API keys in JSON responses
- Never log API keys to console or files
- Never assume environment variables exist without checking
- Never implement without checking existing documentation first