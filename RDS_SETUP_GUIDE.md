# AWS RDS Setup Guide for Sales Analytics Chatbot

## Overview
This guide walks you through connecting your chatbot to **AWS RDS PostgreSQL** instead of local SQLite.

---

## Prerequisites
- ✅ AWS Account (free tier includes RDS)
- ✅ Your local IP address (needed for security group)
- ✅ 10-15 minutes

---

## Step 1: Get Your Local IP Address

**Windows PowerShell:**
```powershell
# Find your public IP
(Invoke-WebRequest -Uri "https://api.ipify.org?format=json").Content | ConvertFrom-Json
```

Save this IP - you'll need it in RDS security group.

---

## Step 2: Create RDS Instance in AWS Console

### 2.1 Go to AWS RDS
1. Log in to [AWS Console](https://console.aws.amazon.com)
2. Search for **RDS** → Click **Databases**
3. Click **Create Database**

### 2.2 Configure Database
| Setting | Value |
|---------|-------|
| **Engine** | PostgreSQL (version 14+) |
| **Template** | Free tier (if eligible) |
| **DB Instance Identifier** | `salesdb` |
| **Master Username** | `postgres` |
| **Master Password** | Create strong password (min 8 chars, mix of uppercase/lowercase/numbers/symbols) |
| **DB Instance Class** | `db.t3.micro` (free tier eligible) |
| **Storage** | `20 GB gp2` (free tier eligible) |
| **Public Accessibility** | **YES** (to connect from your laptop) |
| **Database Name** | `salesdb` |

👉 **IMPORTANT:** Save master password in a secure location (password manager or file)

### 2.3 Create Security Group Rules
After RDS is created (~5-10 mins), configure network access:

1. Click **Connectivity & security** tab
2. Scroll to **VPC security groups** → Click the security group
3. Click **Inbound Rules** → **Edit**
4. **Add Rule:**
   - Type: PostgreSQL
   - Protocol: TCP
   - Port: 5432
   - Source: Your public IP from Step 1 (e.g., `203.0.113.42/32`)
   - OR for testing: `0.0.0.0/0` (less secure, allows anyone)

💾 Save changes

---

## Step 3: Get Your RDS Endpoint

### 3.1 Find Endpoint
1. Go to **RDS Databases** → Click `salesdb`
2. Scroll to **Connectivity & security**
3. Copy the **Endpoint** (looks like: `salesdb.c9akciq32.us-east-1.rds.amazonaws.com`)

This is your `DB_HOST`

---

## Step 4: Fill in Your `.env.local`

Edit `.env.local` and uncomment the RDS section:

```env
# Comment out SQLite
# DATABASE_URL=sqlite:///./sales_analytics.db

# Uncomment and fill RDS details
DB_HOST=salesdb.c9akciq32.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=salesdb
DB_USER=postgres
DB_PASSWORD=your-actual-rds-password
DB_SSL_MODE=require
```

### Values to fill:
| Key | Source | Example |
|-----|--------|---------|
| `DB_HOST` | RDS Endpoint (from Step 3.1) | `salesdb.c9akciq32.us-east-1.rds.amazonaws.com` |
| `DB_PORT` | PostgreSQL standard | `5432` |
| `DB_NAME` | Database you created | `salesdb` |
| `DB_USER` | Master username | `postgres` |
| `DB_PASSWORD` | Master password (saved in Step 2.2) | Your strong password |
| `DB_SSL_MODE` | Security setting | `require` |

---

## Step 5: Seed Sample Data to RDS

### 5.1 Install psycopg2 (PostgreSQL driver)
```powershell
.\.venv\Scripts\Activate.ps1
pip install psycopg2-binary
```

If `psycopg2-binary` fails on Windows, use `pg8000` (already installed):
```powershell
pip install sqlalchemy==1.3.24  # Downgrade needed for Python 3.14
```

### 5.2 Seed Database
Run the database initialization script:
```powershell
python init_db.py
```

This will:
- Create tables (products, customers, sales)
- Insert 200 sample sales records
- Insert 5 products + 5 customers

expected output:
```
Creating database tables...
Populating sample data...
Database initialized successfully!
```

---

## Step 6: Update Backend Server

The backend automatically detects RDS settings:
- If `DB_HOST` and `DB_PASSWORD` are set in `.env.local` → Uses PostgreSQL
- Otherwise → Falls back to SQLite

**No code changes needed!** ✅

But you need to restart the backend:

```powershell
# Kill the running server (Ctrl+C)
# Then restart:
python run_simple_server.py
```

---

## Step 7: Test Connection

### 7.1 Test Backend Health
```powershell
Invoke-WebRequest http://localhost:8000/health -Headers @{"Content-Type"="application/json"}
```

Expected response:
```json
{"status": "ok", "service": "Sales Analytics Chatbot"}
```

### 7.2 Test Chat with RDS Data
```powershell
$body = @{question="What are total sales?"} | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/chat `
  -Body $body `
  -ContentType "application/json"
```

Expected response (from RDS data):
```json
{
  "answer": "Total sales: $XXX,XXX.XX from XXX transactions",
  "sql": "SELECT SUM(revenue) as total_sales, COUNT(*) as num_transactions FROM sales",
  "data_preview": [...]
}
```

---

## Step 8: Verify RDS Connection

### 8.1 Check PostgreSQL Version
```powershell
$connString = "host=salesdb.c9akciq32.us-east-1.rds.amazonaws.com;port=5432;database=salesdb;user id=postgres;password=your-password;sslmode=Require"

python -c "
import psycopg2
try:
    conn = psycopg2.connect('$connString')
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    print(cursor.fetchone())
    conn.close()
    print('✅ RDS Connection Successful!')
except Exception as e:
    print(f'❌ Connection Failed: {e}')
"
```

### 8.2 Query Sample Data
```powershell
python -c "
import psycopg2
conn = psycopg2.connect('host=YOUR_HOST;port=5432;database=salesdb;user=postgres;password=YOUR_PASSWORD;sslmode=require')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM sales;')
print(f'Sales records in RDS: {cursor.fetchone()[0]}')
cursor.execute('SELECT COUNT(*) FROM products;')
print(f'Products in RDS: {cursor.fetchone()[0]}')
conn.close()
"
```

---

## Troubleshooting

### ❌ "Connection timeout"
- **Cause:** Security group inbound rule not set
- **Fix:** Add your IP to RDS security group (Step 3)

### ❌ "Authentication failed"
- **Cause:** Wrong password in `.env.local`
- **Fix:** Check master password saved in Step 2.2

### ❌ "Database does not exist"
- **Cause:** Didn't run `init_db.py` or used wrong `DB_NAME`
- **Fix:** Run `python init_db.py` after updating `.env.local`

### ❌ "FATAL: remaining connection slots are reserved"
- **Cause:** Too many connections to RDS
- **Fix:** Restart backend and browser, or increase max connections in RDS

### ❌ "SSL certificate verify failed"
- **Cause:** `DB_SSL_MODE=require` but connection not encrypted
- **Fix:** Make sure all RDS security rules are applied and RDS is publicly accessible

---

## Switching Back to SQLite

If you want to go back to local SQLite:

1. Edit `.env.local`:
```env
DATABASE_URL=sqlite:///./sales_analytics.db

# Comment out RDS
# DB_HOST=...
# DB_PORT=...
```

2. Restart backend:
```powershell
python run_simple_server.py
```

---

## Cost Estimation (AWS Free Tier)

| Service | Free Tier Limit | Your Usage | Cost |
|---------|-----------------|-----------|------|
| RDS PostgreSQL | 750 hrs/month | ~730 hrs | **FREE** ✅ |
| Data transfer | 1 GB/month | <100 MB | **FREE** ✅ |
| Storage | 20 GB | ~1 MB | **FREE** ✅ |

Total: **$0/month** for 12 months (free tier)

After free tier expires: ~$15-30/month depending on usage.

---

## Next Steps

✅ After RDS is connected:
1. Run chatbot with `npm run dev` (frontend) + `python run_simple_server.py` (backend)
2. Use `start.bat` for one-click startup
3. Verify responses come from RDS (not SQLite)
4. Scale up as needed

Questions? Check the comment in your **`.env.local`** file for quick reference!
