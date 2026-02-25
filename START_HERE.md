# 🎯 Sales Analytics Chatbot – Complete Implementation Guide

**Production-ready full-stack application**: FastAPI backend + React frontend + AWS Bedrock + PostgreSQL RDS

---

## 📦 What You Get

### Backend (app/)
✅ **FastAPI REST API** with CORS, error handling, logging  
✅ **AWS Bedrock (Claude 3)** integration for NL→SQL  
✅ **SQLAlchemy ORM** with PostgreSQL + SQLite support  
✅ **SQL Safety** validation (injection prevention, keyword blocking, table whitelist)  
✅ **Conversation Memory** (last 5 Q/A pairs)  
✅ **Environment-based config** (no hardcoded secrets)  
✅ **Health check endpoint**  

### Frontend (frontend/)
✅ **React 18** + TypeScript + Vite  
✅ **TailwindCSS** responsive UI  
✅ **Chat interface** with message history  
✅ **SQL/Data preview** in responses  
✅ **Real-time error handling**  

### Documentation
✅ **README.md** – Features, setup, architecture  
✅ **QUICKSTART.md** – 5-minute setup guide  
✅ **API.md** – Endpoint reference + examples  
✅ **DEPLOYMENT.md** – Production AWS guide  
✅ **INTEGRATION.md** – SDK examples (Python, JS)  
✅ **MANIFEST.md** – File-by-file guide  

### DevOps
✅ **docker-compose.yml** – One-command setup (PostgreSQL + API)  
✅ **Dockerfile** – Docker image for backend  
✅ **setup.bat / setup.sh** – Automated local setup  
✅ **deploy-aws.sh** – Production deployment script  
✅ **init_db.py** – Database seeding with sample data  
✅ **test_api.py** – API testing suite  

---

## 🚀 Quick Start (Choose One)

### Option A: Windows Batch Script (Easiest)
```bash
cd sales-analytics
setup.bat
# Follow prompts, then:
# Terminal 1: uvicorn app.main:app --reload
# Terminal 2: cd frontend && npm run dev
```

### Option B: Docker (No Python/Node Install)
```bash
docker-compose up
# Backend: http://localhost:8000
# DB: postgres://localhost:5432
```

### Option C: Manual Setup
```bash
# Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

---

## 📂 File Structure

```
sales-analytics/
├── app/                          # Backend
│   ├── main.py                  # FastAPI app, CORS, lifecycle
│   ├── config.py                # .env settings
│   ├── database.py              # SQLAlchemy + PostgreSQL/SQLite
│   ├── models.py                # ORM models (Sales, Products, Customers)
│   ├── schemas.py               # Pydantic request/response
│   ├── services/
│   │   ├── bedrock_service.py   # Claude 3 API client
│   │   ├── sql_generator.py     # NL->SQL + safety validation
│   │   └── analytics_service.py # Orchestration + memory
│   ├── routers/
│   │   └── chat_router.py       # /chat endpoint
│   └── utils/
│       └── prompt_templates.py  # Claude system/user prompts
│
├── frontend/                     # React SPA
│   ├── src/
│   │   ├── api.ts               # Axios API client
│   │   ├── components/
│   │   │   └── ChatBox.tsx      # Main chat UI
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── package.json
│
├── .env.example                  # Template
├── .env.local                    # Local SQLite defaults
├── .env.development              # Dev config template
│
├── requirements.txt              # Python deps
├── docker-compose.yml            # Multi-container setup
├── Dockerfile                    # Backend image
│
├── init_db.py                    # Database initialization + seed
├── test_api.py                   # API test suite
├── setup.bat / setup.sh          # One-command setup
├── deploy-aws.sh                 # Production deployment
│
├── README.md                     # Features & full setup
├── QUICKSTART.md                 # 5-minute guide
├── API.md                        # Endpoint reference
├── DEPLOYMENT.md                 # AWS production guide
├── INTEGRATION.md                # SDK examples
├── MANIFEST.md                   # File guide
└── .gitignore
```

---

## 🔧 Configuration

### Backend (.env)

```bash
# App
APP_NAME=Sales Analytics Chatbot
APP_ENV=development
LOG_LEVEL=INFO

# AWS (required)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Database (pick one)
DATABASE_URL=sqlite:///./sales_analytics.db  # Dev (default)
# OR for PostgreSQL:
# DB_HOST=your-rds.rds.amazonaws.com
# DB_PORT=5432
# DB_NAME=salesdb
# DB_USER=postgres
# DB_PASSWORD=strong-password
# DB_SSL_MODE=require

# Safety
ALLOWED_TABLES=sales,products,customers
MAX_RESULT_ROWS=100
MEMORY_SIZE=5
```

### AWS Setup

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1

# Verify Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
# {"status":"ok","service":"Sales Analytics Chatbot","environment":"development"}
```

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"question":"What were total sales last month?"}'

# Response:
# {
#   "answer": "Total sales last month...",
#   "generated_sql": "SELECT SUM(revenue)...",
#   "data_preview": [{"total": 125430}]
# }
```

### API Test Suite
```bash
python test_api.py
# Runs 5+ test queries, prints results
```

### Swagger UI
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

---

## 📡 API Reference

### POST /chat

**Request:**
```json
{"question": "What were total sales last month?"}
```

**Response:**
```json
{
  "answer": "Total sales last month...",
  "generated_sql": "SELECT SUM(revenue) FROM sales WHERE...",
  "data_preview": [
    {"total_revenue": 125430.50, "transaction_count": 542}
  ]
}
```

**Errors:**
- 400: Invalid question (too short/long)
- 500: Backend/DB failure

### GET /health

**Response:**
```json
{
  "status": "ok",
  "service": "Sales Analytics Chatbot",
  "environment": "development"
}
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│ React SPA       │ localhost:5173
│ TypeScript      │
│ TailwindCSS     │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────────────────┐
│ FastAPI Backend             │ localhost:8000
│ - Chat API                  │
│ - Error handling            │
│ - Logging                   │
│ - CORS enabled              │
└────┬───────────────────┬────┘
     │                   │
     │ boto3            │ SQLAlchemy
     │                   │
     ▼                   ▼
┌──────────────┐  ┌─────────────┐
│ AWS Bedrock  │  │ PostgreSQL  │
│ Claude 3     │  │ or SQLite   │
│ (NL→SQL)     │  │             │
└──────────────┘  └─────────────┘
```

---

## 🔐 Security Features

✅ **SQL Injection Prevention**
- Regex validation of generated SQL
- Blocked DML/DDL keywords (DELETE, DROP, INSERT, UPDATE)
- Table whitelist enforcement
- No raw string concatenation

✅ **Secrets Management**
- All credentials via environment variables (.env)
- AWS IAM role for Bedrock access
- PostgreSQL SSL/TLS encryption
- No hardcoded secrets in code

✅ **API Security**
- CORS restricted to localhost
- Request timeout (30s)
- Error message sanitization
- Structured logging with timestamps

---

## 📊 Example Queries

| Question | SQL Generated |
|----------|---|
| "What were total sales last month?" | SELECT SUM(revenue) FROM sales WHERE sale_date >= CURRENT_DATE - INTERVAL '1 month' |
| "Which region had highest revenue?" | SELECT region, SUM(revenue) FROM sales GROUP BY region ORDER BY SUM(revenue) DESC LIMIT 1 |
| "Show top 5 products by revenue" | SELECT name, SUM(revenue) FROM products JOIN sales ON... GROUP BY name ORDER BY SUM(revenue) DESC LIMIT 5 |
| "Sales by category" | SELECT category, SUM(revenue) FROM products JOIN sales ON... GROUP BY category |

---

## 📈 Performance

| Metric | Target | Notes |
|--------|--------|-------|
| Health Check | <10ms | Instant |
| Chat Response | <10s | 2-3s SQL gen + DB query |
| DB Query | <1s | Indexed columns |
| Frontend Load | <3s | Vite optimized |
| Bedrock API | ~2-3s | AWS latency |

---

## 🚀 Production Deployment (AWS)

### Prerequisites
```bash
- EC2 instance (t3.medium+, Ubuntu 22.04)
- RDS PostgreSQL 14+
- AWS IAM role with Bedrock access
- S3 bucket for frontend
- CloudFront distribution
```

### Steps
1. **Backend**: Deploy to EC2 with SystemD service
2. **Database**: RDS PostgreSQL (SSL enabled)
3. **Frontend**: Build & upload to S3 + CloudFront
4. **API Gateway**: Optional JWT auth + rate limiting

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed instructions.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Backend won't start** | Check port 8000 free: `lsof -i :8000` |
| **psycopg2 import error** | Ensure pip install successful, try pg8000 driver |
| **DB connection refused** | Check RDS endpoint, security group, credentials |
| **Bedrock access denied** | Verify AWS creds, IAM role, region |
| **Frontend blank page** | Check console errors, backend running, CORS |
| **SQL injection error** | Questions are natural language, not SQL |

---

## 📚 Documentation

| File | Content |
|------|---------|
| **README.md** | Full feature overview, setup instructions |
| **QUICKSTART.md** | 5-minute getting started |
| **API.md** | Endpoint reference, example queries |
| **DEPLOYMENT.md** | AWS production deployment guide |
| **INTEGRATION.md** | Python/JS SDK examples, webhooks |
| **MANIFEST.md** | File-by-file breakdown |
| **This file** | Complete implementation guide |

---

## 🛠️ Useful Commands

```bash
# Backend
uvicorn app.main:app --reload              # Dev server
python init_db.py                          # Seed database
python test_api.py                         # Run API tests
gunicorn app.main:app --workers 4          # Production

# Frontend
npm install                                # Install deps
npm run dev                                # Dev server
npm run build                              # Production build
npm run preview                            # Preview build

# Database
python -c "from app.config import get_settings; print(get_settings())"  # Check config
psql -h host -U user -d db                 # Connect to PostgreSQL

# Docker
docker-compose up                          # Start all services
docker-compose down -v                     # Stop & clean
docker-compose logs -f api                 # View logs
```

---

## 💡 Key Features

1. **Natural Language to SQL**: Ask business questions, get SQL queries
2. **Safety First**: SQL injection prevention, keyword blocking, table whitelisting
3. **Conversation Memory**: Last 5 Q/A pairs stored for context
4. **Business Summary**: Claude generates natural language answers from data
5. **Full Stack**: React UI, FastAPI backend, PostgreSQL data
6. **Secure**: Environment-based config, no hardcoded secrets
7. **Observable**: Logging, error handling, health checks
8. **Scalable**: SQLAlchemy connection pooling, async request handling
9. **Production Ready**: Docker, systemd service, deployment guide

---

## 📞 Support Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **AWS Bedrock**: https://docs.aws.amazon.com/bedrock/
- **React**: https://react.dev
- **Vite**: https://vitejs.dev

---

## 🎓 Next Steps

1. **Start Local**: Run `setup.bat` or `docker-compose up`
2. **Explore Data**: Open http://localhost:5173, try sample queries
3. **Customize**: Edit prompts in `app/utils/prompt_templates.py`
4. **Add Tables**: Add models in `app/models.py`, update `ALLOWED_TABLES`
5. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md) for AWS

---

## ✅ Requirements Met

- [x] FastAPI backend
- [x] React frontend with TailwindCSS
- [x] AWS Bedrock (Claude 3) NL→SQL
- [x] SQLAlchemy ORM + PostgreSQL/SQLite
- [x] SQL safety validation
- [x] Conversation memory (5 pairs)
- [x] Error handling & logging
- [x] Environment-based config
- [x] CORS support
- [x] Health check endpoint
- [x] Production deployment guide
- [x] Full API documentation
- [x] Integration examples
- [x] Docker support

---

**Status**: ✅ Production-Ready  
**Last Updated**: February 2025  
**Version**: 1.0.0

Start with `setup.bat` (Windows) or `docker-compose up` (all platforms).
