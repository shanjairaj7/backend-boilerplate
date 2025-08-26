# Third Party API Integration Guide

This documentation provides guidance for integrating external APIs into your backend application.

## 🏗️ INTEGRATION WORKFLOW

When a user requests third-party API integration, the LLM must follow this workflow:

### Step 1: Research the API

**Mandatory**: Use web search to understand the API before implementation

- Use `<action type="web_search" query="[API_NAME] API documentation endpoints authentication key">`
- Identify: base URL, authentication method, required API keys, main endpoints, response format
- Understand: rate limits, error handling, how to get API keys

### Step 2: Plan Integration

Based on research findings:

- Create dedicated service file in `backend/routes/[service_name]_api.py`
- Plan environment variables needed for API keys
- Design request/response data models
- Plan error handling for API failures

## 🛠️ IMPLEMENTATION REQUIREMENTS

### Step 3: Backend Implementation

- Load API keys from environment variables using `os.getenv()`
- Create FastAPI router with appropriate prefix `/api/[service-name]`
- Use `httpx.AsyncClient` for async API calls
- Create Pydantic models for request/response data
- Implement comprehensive error handling for API failures

### Step 4: Restart Backend
After implementation, restart the backend to load new routes:
- Use `<action type="restart_backend"/>` to deploy updated backend with new API integration

### Step 5: Environment Configuration

- All API keys must come from environment variables, never hardcoded
- Use descriptive environment variable names like `WEATHER_API_KEY`
- Handle missing API keys gracefully with helpful error messages

## 📋 COMMON INTEGRATION PATTERNS

### Weather APIs

- Research: OpenWeatherMap, WeatherAPI, or similar
- Typical auth: API key in query parameter or header
- Common endpoints: current weather, forecasts by city/coordinates

### Financial/Trading APIs

- Research: Alpha Vantage, IEX Cloud, Finnhub
- Typical auth: API key parameter
- Common endpoints: stock quotes, historical data, market news

### News APIs

- Research: NewsAPI, Guardian API, Reddit API
- Typical auth: API key in header
- Common endpoints: search articles, top headlines, by category

## 🔐 SECRET MANAGEMENT

### Step 6: User Setup Instructions

After implementing the API integration, provide these instructions to the user:

**API Key Setup Required**:

1. **Get API Key**: Visit the API provider's website, sign up, generate API key
2. **Configure in App**: Go to Dashboard → Backend → add the secret
   - **Secret Name**: `[API_KEY_ENV_NAME]`
   - **Secret Value**: `[Your actual API key]`
3. **Backend Restart**: Backend automatically restarts with new environment variables

## 🚨 MANDATORY REQUIREMENTS

**Only integrate third-party APIs when the user explicitly requests it. Do not integrate APIs unless specifically asked.**

**Must Do**:

1. **Web Search**: Research API before any implementation
2. **Environment Variables**: All keys from `os.getenv()`, never hardcoded
3. **Error Handling**: Handle API failures, rate limits, invalid responses
4. **Backend Restart**: Use `<action type="restart_backend"/>` after implementing API
5. **User Instructions**: Clear setup guide for API key configuration

**Must Not Do**:

- Never integrate APIs unless user specifically requests it
- Never hardcode API keys in code
- Don't implement without researching the API first
- Don't ignore rate limits or error responses
