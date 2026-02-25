# Git Setup & Push Guide

## 🔒 Protected Files (Already in .gitignore)

These files will **NOT** be pushed to Git:
- ✅ `.env`, `.env.local`, `.env.production` - Environment variables
- ✅ `.venv/` - Virtual environment (large, user-specific)
- ✅ `*.db`, `*.sqlite` - Database files with sample data
- ✅ `node_modules/` - Frontend dependencies (large)
- ✅ `.aws/`, `*.key`, `*.pem` - AWS credentials and keys
- ✅ `__pycache__/`, `*.pyc` - Python compiled files
- ✅ `dist/`, `build/` - Build outputs

## 📋 Steps to Push to Git Repository

### First Time Setup (One Time Only)

1. **Configure Git identity** (if not already done):
   ```powershell
   git config --global user.name "Your Name"
   git config --global user.email "your.email@company.com"
   ```

2. **Initialize Git repository** (in sales-analytics folder):
   ```powershell
   cd "C:\Users\Sejal Kumari\OneDrive - E-SOLUTIONS IT SERVICES PRIVATE LIMITED\Documents\sales-analytics"
   git init
   ```

3. **Create repository on GitHub/GitLab/Bitbucket**:
   - Go to GitHub.com (or your Git provider)
   - Click "New Repository"
   - Name it: `sales-analytics-chatbot`
   - **DO NOT** initialize with README (you already have code)
   - Copy the repository URL (e.g., `https://github.com/username/sales-analytics-chatbot.git`)

4. **Add remote repository**:
   ```powershell
   git remote add origin YOUR_REPOSITORY_URL
   # Example: git remote add origin https://github.com/yourusername/sales-analytics-chatbot.git
   ```

### Every Time You Want to Push Changes

5. **Check what files will be committed**:
   ```powershell
   git status
   ```
   - Verify no `.env`, `.db`, or sensitive files appear
   - Green = will be committed, Red = untracked/modified

6. **Add all files to staging**:
   ```powershell
   git add .
   ```

7. **Commit with a message**:
   ```powershell
   git commit -m "Initial commit: Sales Analytics Chatbot with FastAPI and React"
   ```
   - Use descriptive messages like:
     - `"Add database seeding script"`
     - `"Fix frontend CORS configuration"`
     - `"Update README with deployment instructions"`

8. **Push to GitHub** (first time):
   ```powershell
   git push -u origin main
   ```
   - Or if your default branch is `master`:
     ```powershell
     git push -u origin master
     ```

9. **Push subsequent changes**:
   ```powershell
   git push
   ```

### If You Need to Switch Branch Name

If Git created `master` but you want `main`:
```powershell
git branch -M main
git push -u origin main
```

## 🔍 Verify Protection Works

Before first push, check what Git sees:
```powershell
git status --ignored
```

You should see (in red/ignored section):
- `.venv/`
- `sales_analytics.db`
- `.env`, `.env.local`
- `node_modules/`

## ⚠️ Important Security Notes

1. **Never commit `.env` files** - They contain AWS credentials, database passwords
2. **Database file is ignored** - Collaborators must run `init_db_simple.py` locally
3. **Virtual environment ignored** - Collaborators run `pip install -r requirements.txt`
4. **Frontend deps ignored** - Collaborators run `npm install` in frontend/

## 📝 What WILL Be Pushed (Safe Files)

- ✅ All Python source code (`app/`, `*.py`)
- ✅ All React/TypeScript code (`frontend/src/`)
- ✅ Configuration templates (`.env.example`)
- ✅ Requirements files (`requirements.txt`, `package.json`)
- ✅ Documentation (`*.md` files)
- ✅ Dockerfile, docker-compose.yml
- ✅ Scripts (`init_db.py`, `run_simple_server.py`)

## 🤝 Collaborator Onboarding

When someone clones your repository, they need to:

1. Clone the repo:
   ```powershell
   git clone YOUR_REPOSITORY_URL
   cd sales-analytics-chatbot
   ```

2. Set up backend:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Create `.env` file (copy from `.env.example` and fill in their AWS credentials)

4. Seed database:
   ```powershell
   python init_db_simple.py
   ```

5. Set up frontend:
   ```powershell
   cd frontend
   npm install
   ```

6. Run the app (two terminals):
   ```powershell
   # Terminal 1: Backend
   python run_simple_server.py
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 🔄 Common Git Workflow

```powershell
# Pull latest changes from team
git pull

# Make your changes to code...

# Check what changed
git status
git diff

# Stage and commit
git add .
git commit -m "Descriptive message about your changes"

# Push to shared repository
git push
```

## 🆘 Troubleshooting

**If you accidentally committed sensitive files:**
```powershell
# Remove from Git but keep local file
git rm --cached .env
git rm --cached sales_analytics.db
git commit -m "Remove sensitive files"
git push

# Then rotate all exposed credentials immediately!
```

**If remote rejects push (conflict):**
```powershell
git pull --rebase
# Resolve conflicts if any
git push
```

**Check what will be ignored:**
```powershell
git check-ignore -v .env
git check-ignore -v .venv/
```

## 📚 Useful Git Commands

- `git status` - See what's changed
- `git log --oneline` - See commit history
- `git diff` - See exact changes
- `git branch` - See current branch
- `git checkout -b feature/new-feature` - Create new branch
- `git clone URL` - Clone repository
