# 🚀 AI Chatbot Deployment Guide

## Overview
This document provides complete deployment instructions for the AI Chatbot Platform API. The application is a multi-tenant FastAPI-based chatbot with MongoDB integration and Google Gemini AI capabilities.

---

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- MongoDB database (local or cloud)
- Google API account with Gemini access
- Web server (for production deployment)

### Required Services
1. **MongoDB Database**
   - Local MongoDB instance, or
   - MongoDB Atlas (cloud)
   - Database name: `ai_chat_bot` (configurable)

2. **Google API Services**
   - Google AI/Gemini API key
   - Access to `gemini-1.5-flash` model
   - Access to `embedding-001` model

---

## ⚙️ Configuration Values to Change

### 1. Environment Variables (.env file)

Create a `.env` file in the root directory with the following values:

```bash
# Database Configuration
MONGO_URL="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority"
MONGO_DB_NAME="ai_chat_bot"

# Google AI/Gemini Configuration
GOOGLE_API_KEY="AIzaSy..."  # Your Google API key
GEMMA_EMBEDDING_MODEL="embedding-001"
```

### 2. Production Environment Variables

For deployment platforms (Render, Railway, Heroku, etc.), set these environment variables:

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `MONGO_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/ai_chat_bot` |
| `MONGO_DB_NAME` | Database name | `ai_chat_bot` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSyDKzpg3Z8aLmY_lIoXRu7svHpDafmT_DhI` |
| `GEMMA_EMBEDDING_MODEL` | Embedding model name | `embedding-001` |

### 3. MongoDB Setup

#### For MongoDB Atlas (Recommended for production):
1. Create a MongoDB Atlas account
2. Create a new cluster
3. Create a database user with read/write permissions
4. Whitelist your deployment platform's IP addresses
5. Get the connection string and replace `<username>`, `<password>`, and `<cluster>` placeholders

#### For Local MongoDB:
```bash
MONGO_URL="mongodb://localhost:27017"
```

### 4. Google API Key Setup

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create or select a project
3. Enable the Generative Language API
4. Generate an API key
5. Copy the API key to your environment variables

---

## 🛠️ Deployment Steps

### Local Development Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_chat_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Production Deployment (Render/Railway/Heroku)

#### On Render:
1. Connect your GitHub repository
2. Choose "Web Service"
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: Add all variables from the table above
4. Deploy

#### On Railway:
1. Connect your GitHub repository
2. Set environment variables in the Variables tab
3. Railway will auto-detect Python and deploy

#### On Heroku:
1. Create a new Heroku app
2. Set Config Vars with all environment variables
3. Deploy via Git or GitHub integration

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-chatbot .
docker run -p 8000:8000 --env-file .env ai-chatbot
```

---

## 🔧 Post-Deployment Configuration

### 1. Health Check
Test the deployment by accessing:
```
GET https://your-domain.com/
```
Expected response:
```json
{"message": "Chatbot API is running"}
```

### 2. Create Your First App
```bash
curl -X POST "https://your-domain.com/api/v1/admin/apps" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Chatbot",
    "description": "My first chatbot application",
    "googleApiKey": "your-google-api-key",
    "welcomeMessage": {"en": "Hello! How can I help you today?"},
    "languages": ["en"]
  }'
```

### 3. Test Chat Functionality
```bash
curl -X POST "https://your-domain.com/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -H "X-App-ID: <your-app-id>" \
  -d '{"message": "Hello"}'
```

---

## 🚨 Security Considerations

### Production Security Checklist:
- [ ] Use HTTPS in production
- [ ] Set strong MongoDB credentials
- [ ] Restrict MongoDB network access
- [ ] Keep Google API keys secure (never commit to Git)
- [ ] Use environment variables for all secrets
- [ ] Enable MongoDB authentication
- [ ] Set up proper CORS policies if needed
- [ ] Monitor API usage and set rate limits

### Environment Variable Security:
- Never commit `.env` files to version control
- Use your deployment platform's secure environment variable storage
- Rotate API keys regularly
- Monitor for unusual API usage

---

## 📊 Monitoring & Maintenance

### Health Monitoring
- Monitor the `/` endpoint for service availability
- Set up alerts for MongoDB connection issues
- Monitor Google API usage and quotas

### Logs
The application uses Python's logging module. In production:
- Set up log aggregation (Papertrail, Logtail, etc.)
- Monitor for Gemini API errors
- Track embedding generation failures

### Database Maintenance
- Regular MongoDB backups
- Monitor database size and performance
- Index optimization for chat_sessions and app_content collections

---

## 🐛 Troubleshooting

### Common Issues:

1. **ModuleNotFoundError: No module named 'aiofiles'**
   - Solution: Already fixed in requirements.txt

2. **MongoDB Connection Error**
   - Check MONGO_URL format
   - Verify network access and credentials
   - Ensure MongoDB cluster is running

3. **Google API Error: 400 Bad Request**
   - Verify GOOGLE_API_KEY is correct
   - Check API quotas and billing
   - Ensure Generative Language API is enabled

4. **Deployment fails with "Port already in use"**
   - Use `$PORT` environment variable in production
   - Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Debug Commands:
```bash
# Check environment variables
python -c "from app.config import settings; print(settings.dict())"

# Test MongoDB connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('your-mongo-url').admin.command('ismaster'))"

# Test Google API
python -c "import httpx; import asyncio; asyncio.run(httpx.get('https://generativelanguage.googleapis.com/v1beta/models?key=your-api-key'))"
```

---

## 📞 Support

For deployment issues:
1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Test individual components (database, API) separately
4. Consult the DEPLOYMENT_FIX.md for known issues

---

## 📝 Summary

**Key Configuration Changes for Deployment:**
1. ✅ Set `MONGO_URL` with your MongoDB connection string
2. ✅ Set `GOOGLE_API_KEY` with your Google Gemini API key
3. ✅ Configure `MONGO_DB_NAME` (default: "ai_chat_bot")
4. ✅ Set `GEMMA_EMBEDDING_MODEL` (default: "embedding-001")
5. ✅ Use proper start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The application is now ready for production deployment with multi-tenant support, document processing, guardrails, and Google Gemini AI integration!