# Quick Start Guide

## ⚡ 5-Minute Local Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- AWS credentials (for Bedrock, optional for local SQLite testing)

---

## Option 1: Quick Setup (Windows)

```bash
# 1. Clone/extract project
cd sales-analytics

# 2. Run setup script
setup.bat

# 3. Configure .env
notepad .env
# Edit DB settings and AWS credentials

# 4. Start backend (terminal 1)
.venv\Scripts\activate
uvicorn app.main:app --reload

# 5. Start frontend (terminal 2)
cd frontend
npm install
npm run dev

# 6. Open browser
# http://localhost:5173
```

---

## Option 2: Docker Compose (All-in-One)

No Python/Node installation needed!

```bash
# 1. Clone/extract project
cd sales-analytics

# 2. Create .env
copy .env.example .env
# Edit AWS_REGION, BEDROCK_MODEL_ID

# 3. Start containers
docker-compose up

# 4. Initialize DB
docker-compose exec api python init_db.py

# 5. Open browser
# Frontend: http://localhost:5173 (requires separate setup)
# Backend: http://localhost:8000

# 6. Cleanup
docker-compose down -v
```

---

## Option 3: Manual Setup (Full Control)

### Backend

```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env
copy .env.example .env

# 4. Configure .env (choose ONE database):

# Option A: SQLite (no setup needed)
DATABASE_URL=sqlite:///./sales_analytics.db

# Option B: PostgreSQL (RDS)
DB_HOST=your-rds.rds.amazonaws.com
DB_PORT=5432
DB_NAME=salesdb
DB_USER=postgres
DB_PASSWORD=strong-password
DB_SSL_MODE=require

# 5. Initialize database
python init_db.py

# 6. Start backend
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs for Swagger UI

# 7. Test health
curl http://localhost:8000/health
```

### Frontend

```bash
# In new terminal

# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# 4. Open http://localhost:5173
```

### Test Chat

```bash
# Test via cURL
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What were total sales last month?\"}"

# Or use UI at http://localhost:5173
```

---

## 🔧 Configuration

### Backend (.env)

```bash
# App
APP_NAME=Sales Analytics Chatbot
APP_ENV=development
LOG_LEVEL=INFO

# AWS (required for Bedrock)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Database (choose one)

# SQLite (recommended for dev)
DATABASE_URL=sqlite:///./sales_analytics.db

# PostgreSQL RDS
# DB_HOST=...rds.amazonaws.com
# DB_PORT=5432
# DB_NAME=salesdb
# DB_USER=postgres
# DB_PASSWORD=***

# Safety
ALLOWED_TABLES=sales,products,customers
MAX_RESULT_ROWS=100
MEMORY_SIZE=5
```

### AWS Credentials

Set via environment (recommended):

```bash
# On Windows
set AWS_ACCESS_KEY_ID=your-key
set AWS_SECRET_ACCESS_KEY=your-secret

# On macOS/Linux
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

Or use `~/.aws/credentials`:

```
[default]
aws_access_key_id = your-key
aws_secret_access_key = your-secret
```

---

## 📁 Project Layout

```
sales-analytics/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy + engine
│   ├── models.py            # ORM models (Sales, Products, Customers)
│   ├── schemas.py           # Request/Response models
│   ├── services/
│   │   ├── bedrock_service.py   # Claude 3 API calls
│   │   ├── sql_generator.py     # NL → SQL converter
│   │   └── analytics_service.py # Main orchestration
│   ├── routers/
│   │   └── chat_router.py   # /chat endpoint
│   └── utils/
│       └── prompt_templates.py  # Prompts for Claude
├── frontend/
│   ├── src/
│   │   ├── components/ChatBox.tsx  # Chat UI
│   │   ├── api.ts                  # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── ...
├── init_db.py               # DB seeding script
├── requirements.txt         # Python packages
├── .env.example
├── docker-compose.yml       # Optional Docker setup
├── Dockerfile
├── setup.bat / setup.sh     # Quick setup scripts
├── README.md                # Full documentation
├── API.md                   # API reference
├── DEPLOYMENT.md            # Production guide
└── QUICKSTART.md           # THIS FILE
```

---

## 🧪 Test Queries

Try these in the UI or via cURL:

| Query | Purpose |
|-------|---------|
| "What were total sales last month?" | Basic aggregation |
| "Which region had the highest revenue?" | Regional breakdown |
| "Show top 5 products by revenue" | Product ranking |
| "Compare Q3 vs Q4 sales" | Period comparison |
| "Sales by category" | Category analysis |

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is free
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Check .env is valid
python -c "from app.config import get_settings; print(get_settings())"

# Check database connection
python init_db.py
```

### Frontend blank page

```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check console for errors
# Open DevTools (F12) → Console tab

# 3. Check port 5173 is free
# Try: npm run dev -- --port 5174
```

### Bedrock "AccessDenied"

```bash
# 1. Check AWS credentials are set
aws sts get-caller-identity

# 2. Verify IAM permissions
# CloudFormation/IAM → Check `bedrock:InvokeModel` allow

# 3. Check region
echo $AWS_REGION  # Should be us-east-1 for Claude 3
```

### PostgreSQL connection failed

```bash
# 1. Test RDS connectivity
psql -h your-rds.rds.amazonaws.com -U postgres -d salesdb

# 2. Check security group allows EC2 (port 5432)

# 3. Check .env has correct host/port/password

# 4. Fall back to SQLite
# Set: DATABASE_URL=sqlite:///./sales_analytics.db
```

---

## 📈 Next Steps

1. **Explore Data**
   - Open http://localhost:5173
   - Try various sales queries
   - View generated SQL

2. **Customize Prompts**
   - Edit `app/utils/prompt_templates.py`
   - Adjust system/user prompts for your domain

3. **Add Table**
   - Add model in `app/models.py`
   - Add to `ALLOWED_TABLES` in `.env`
   - Re-run `python init_db.py`

4. **Production Deployment**
   - See `DEPLOYMENT.md` for AWS setup
   - Use RDS instead of SQLite
   - Deploy backend to EC2, frontend to S3

5. **Add Authentication**
   - Implement JWT in `app/routers/chat_router.py`
   - Restrict via API Gateway

---

## 📚 Documentation

- **[README.md](README.md)** – Full feature overview
- **[API.md](API.md)** – Endpoint reference & examples
- **[DEPLOYMENT.md](DEPLOYMENT.md)** – Production guide for AWS
- **FastAPI Docs** – http://localhost:8000/docs

---

## ⚙️ Commands Cheat Sheet

```bash
# Backend
uvicorn app.main:app --reload          # Start dev server
python init_db.py                      # Seed database
python -c "from app.config import get_settings; print(get_settings())"  # Check config

# Frontend
npm install                            # Install deps
npm run dev                            # Start dev server
npm run build                          # Production build

# Docker
docker-compose up                      # Start all services
docker-compose down -v                 # Stop and remove volumes
docker-compose logs -f api            # View logs

# Testing
curl http://localhost:8000/health     # Check backend
curl http://localhost:5173            # Check frontend
```

---

## 💡 Tips

- **SQLite dev mode**: No setup needed, data stored in `sales_analytics.db`
- **Bedrock costs**: ~$0.003 per 1K input tokens, test with small questions
- **Frontend build**: `npm run build` creates optimized `dist/` folder for deployment
- **Logs**: Tail backend logs for debugging: `uvicorn app.main:app --reload --log-level DEBUG`
- **Swagger UI**: http://localhost:8000/docs is interactive API explorer

---

**Need help?** Check error messages in terminal/browser console. All errors logged with timestamps.

**Ready for production?** See [DEPLOYMENT.md](DEPLOYMENT.md) for AWS setup.
