# Quick Reference - Sales Analytics Chatbot

## 🚀 Start App (Easy Way)

Double-click: `start.bat`

## 🚀 Start App (Manual Way)

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
python run_simple_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

**Open Browser:**
- Frontend: http://localhost:5173
- Backend Health: http://localhost:8000/health

## 🛑 Stop App

Press `Ctrl + C` in both terminals (or close terminal windows)

## 🔄 Push to Git (Step by Step)

```powershell
# 1. See what changed
git status

# 2. Add all files
git add .

# 3. Commit with message
git commit -m "Your descriptive message here"

# 4. Push to GitHub
git push
```

## 🔒 Protected Files (Never Pushed)

- `.env`, `.env.local` - Credentials
- `.venv/` - Virtual environment
- `sales_analytics.db` - Database
- `node_modules/` - Frontend dependencies
- `*.key`, `*.pem` - Keys

## 📋 First Time Git Setup

```powershell
# Initialize Git
git init

# Add remote (replace URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# First push
git add .
git commit -m "Initial commit: Sales Analytics Chatbot"
git push -u origin main
```

## 🤝 Team Member Setup (Clone Repository)

```powershell
# 1. Clone
git clone REPOSITORY_URL
cd sales-analytics-chatbot

# 2. Backend setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 3. Create .env file (copy .env.example and add credentials)

# 4. Seed database
python init_db_simple.py

# 5. Frontend setup
cd frontend
npm install
cd ..

# 6. Run app
# Use start.bat or manual commands above
```

## 📁 Project Structure

```
sales-analytics/
├── app/                    # Backend API code
├── frontend/               # React UI code
├── .venv/                  # Virtual environment (ignored)
├── .env                    # Secrets (ignored)
├── sales_analytics.db      # Database (ignored)
├── requirements.txt        # Python dependencies
├── run_simple_server.py    # Backend server
├── init_db_simple.py       # Database seeding
├── start.bat               # Quick start script
├── GIT_SETUP.md           # Detailed Git guide
└── README.md              # Full documentation
```

## 💡 Sample Questions to Test

- "What are total sales?"
- "Show me sales by region"
- "What are the top products?"
- "Show sales trend"
- "How many transactions?"

## 🐛 Troubleshooting

**Backend won't start:**
- Check if `.venv` exists: `pip install -r requirements.txt`
- Check if database exists: `python init_db_simple.py`

**Frontend won't start:**
- Check node_modules: `cd frontend && npm install`

**Can't push to Git:**
- Check remote: `git remote -v`
- Add remote: `git remote add origin URL`

**Accidentally committed secrets:**
```powershell
git rm --cached .env
git commit -m "Remove secrets"
git push
# THEN ROTATE ALL CREDENTIALS!
```

## 📞 Support

Check these files for details:
- **GIT_SETUP.md** - Complete Git workflow
- **README.md** - Full project documentation
- **DEPLOYMENT.md** - AWS deployment guide
