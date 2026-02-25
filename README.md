# Sales Analytics Chatbot – Full Stack

Production-ready **FastAPI** backend + **React** frontend for natural language sales analytics using AWS Bedrock (Claude 3) and Amazon RDS (PostgreSQL).

## 🎯 Features

### Backend
- FastAPI with async request handling
- Amazon Bedrock (Claude 3 Sonnet) NL→SQL conversion
- SQLAlchemy ORM + PostgreSQL
- SQL safety validation (SELECT-only, table whitelisting, row limit)
- Conversation memory (last 5 Q/SQL pairs)
- Structured error handling & logging
- CORS support for frontend
- Health check endpoint

### Frontend
- React 18 + TypeScript + Vite
- TailwindCSS for styling
- Axios for API calls
- Message history with SQL/data preview
- Real-time error handling
- Responsive design

## 📋 Requirements

- Python 3.10+
- Node.js 16+ (for frontend)
- AWS credentials with Bedrock access
- PostgreSQL 12+ (Amazon RDS)

## 🚀 Setup & Run

### 1. Backend Setup

#### Clone/Extract & Install

```bash
cd sales-analytics
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

#### Configure Environment

```bash
copy .env.example .env
```

Edit `.env` with your RDS and AWS details:

```bash
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_PORT=5432
DB_NAME=salesdb
DB_USER=postgres
DB_PASSWORD=your-strong-password
DB_SSL_MODE=require
```

#### Initialize Database

```bash
python init_db.py
```

Output should show:
```
Creating database tables...
✓ Tables created
Seeding sample data...
✓ Inserted 5 products
✓ Inserted 5 customers
✓ Inserted 200 sales records
✓ Database seeding complete!
```

#### Start Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Test health: `curl http://localhost:8000/health`

---

### 2. Frontend Setup

Open a new terminal:

```bash
cd sales-analytics/frontend
npm install
npm run dev
```

Expected output:
```
VITE v5.0.0  ready in XXX ms

➜  Local:   http://localhost:5173/
```

Open browser to **http://localhost:5173/**

---

## 🧪 Test Chat

### Via UI
1. Navigate to http://localhost:5173/
2. Type: "What were total sales last month?"
3. View response, SQL, and data table

### Via cURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Which region had highest revenue in Q4?\"}"
```

Response:
```json
{
  "answer": "The West region achieved the highest Q4 revenue...",
  "generated_sql": "SELECT region, SUM(revenue) FROM sales WHERE ...",
  "data_preview": [
    {"region": "West", "total_revenue": 45230.50}
  ]
}
```

## 📁 Project Structure

```
sales-analytics/
  ├── app/
  │   ├── main.py                 # FastAPI app + lifespans
  │   ├── config.py               # Settings & env vars
  │   ├── database.py             # SQLAlchemy setup
  │   ├── models.py               # ORM models
  │   ├── schemas.py              # Pydantic request/response
  │   ├── services/
  │   │   ├── bedrock_service.py  # Claude 3 API client
  │   │   ├── sql_generator.py    # NL→SQL converter
  │   │   └── analytics_service.py# Business logic
  │   ├── routers/
  │   │   └── chat_router.py      # /chat endpoint
  │   └── utils/
  │       └── prompt_templates.py # System/user prompts
  ├── frontend/
  │   ├── src/
  │   │   ├── components/ChatBox.tsx
  │   │   ├── api.ts
  │   │   ├── App.tsx
  │   │   ├── main.tsx
  │   │   └── index.css
  │   ├── index.html
  │   ├── vite.config.ts
  │   ├── tsconfig.json
  │   ├── tailwind.config.js
  │   └── package.json
  ├── init_db.py                  # DB seed script
  ├── requirements.txt            # Python deps
  ├── .env.example
  └── README.md
```

## 🔐 Security Notes

- Database credentials via `.env` (never commit)
- AWS IAM role for Bedrock access (restrict to Claude 3)
- Read-only DB user recommended
- SQL validation prevents injection
- CORS configured for localhost

## 🌐 Production Deployment

### Backend (Gunicorn + EC2)

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (S3 + CloudFront)

```bash
npm run build
# Upload dist/ to S3
```

### RDS Setup
- Create PostgreSQL 14+ instance
- Enable SSL (DB_SSL_MODE=require)
- Whitelist EC2 security group

## 📝 Example Queries

- "What were total sales last month?"
- "Which region had highest revenue in Q4?"
- "Show top 5 products by revenue"
- "Compare this quarter vs last quarter revenue"
- "Sales by category"

## 🐛 Troubleshooting

**`psycopg2` import error**: Ensure `pip install -r requirements.txt` completed successfully. If on Windows and psycopg2-binary fails, `pg8000` is a fallback pure-Python driver.

**`Connection refused` on DB**: Check `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` in `.env` and RDS security group allows EC2.

**Bedrock `AccessDenied`**: Verify AWS credentials are set and IAM role grants `bedrock:InvokeModel` permission.

**Frontend blank white screen**: Check browser console; backend likely not accessible. Ensure both servers running on correct ports.

## 📚 References

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [AWS Bedrock Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
- [React + TypeScript](https://react.dev)
- [Vite Docs](https://vitejs.dev)
