# Git Workflow & Deployment Guide

This document outlines the development and deployment workflow for GoalGPT.

## Architecture Overview

GoalGPT uses a **Development/Production Split Architecture**:

- **`/app/`** - Clean development environment for AI-assisted coding
- **`/api/`** - Production-ready API with debugging, monitoring, and advanced features
- **`scripts/`** - Automation tools to sync between environments

## Git Workflow

### Branch Strategy

```
main           ←  Production releases, auto-deployed
├── develop    ←  Integration branch for features  
├── feature/*  ←  Individual feature branches
└── hotfix/*   ←  Critical production fixes
```

### Development Process

1. **Feature Development**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   
   # Work in /app/ directory for clean AI-assisted development
   uvicorn app.main:app --reload
   
   # Commit your changes
   git add .
   git commit -m "feat: add new feature"
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Open PR from `feature/your-feature-name` → `develop`
   - CI/CD will automatically test both frontend and backend
   - Code review and approval required

3. **Integration Testing**
   ```bash
   # On develop branch
   git checkout develop
   git merge feature/your-feature-name
   
   # Test the sync process
   python scripts/sync_to_production.py
   python scripts/validate_sync.py
   
   # Test production build
   docker-compose up --build
   ```

4. **Production Release**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   
   # This triggers automatic deployment via CI/CD
   ```

## Local Development

### Quick Start
```bash
# Backend development (use this for AI pair programming)
cd app/
uvicorn main:app --reload

# Frontend development
cd web/
npm run dev

# Full stack with Docker
docker-compose up --build
```

### Development Commands
```bash
# Backend (in /app/)
uvicorn main:app --reload        # Start dev server
pytest                          # Run tests
mypy app/                       # Type checking
flake8 app/                     # Linting

# Frontend (in /web/)
npm run dev                     # Start dev server
npm run build                   # Build for production
npm run lint                    # ESLint
npm run type-check              # TypeScript checking
```

## Deployment Process

### Automatic Deployment (Recommended)

1. **Push to main** - Triggers automatic deployment
2. **CI/CD Pipeline** automatically:
   - Runs all tests (backend + frontend)
   - Syncs `/app/` → `/api/` with production features
   - Validates the sync
   - Builds Docker images
   - Deploys to production

### Manual Deployment

```bash
# 1. Sync development to production
python scripts/sync_to_production.py

# 2. Validate sync
python scripts/validate_sync.py

# 3. Build and deploy
docker-compose up --build -d
```

## Sync Process Details

### What Gets Synced

**Core Files** (`/app/` → `/api/`):
- `main.py` - Base API + production endpoints (`/api/tree`, `/gpt/goals`)
- `db.py` - Base functions + production debugging & JWT validation
- `requirements.txt` - Identical dependencies
- `__init__.py` - Module initialization

**Production Enhancements Added**:
- Debug logging with environment masking
- JWT token expiration warnings
- Database connectivity testing
- Complex tree visualization endpoint
- GPT integration endpoints
- Performance monitoring

### Validation Checks

The `validate_sync.py` script ensures:
- ✅ All core files exist in both environments
- ✅ Requirements.txt are identical
- ✅ Production features are present in `/api/`
- ✅ Core business logic is consistent
- ✅ No development artifacts in production

## CI/CD Pipeline

### Triggered On
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

### Pipeline Stages

1. **Backend Tests**
   - Python 3.11 environment
   - Install dependencies
   - Lint with flake8
   - Type check with mypy
   - Run pytest

2. **Frontend Tests**
   - Node.js 18 environment
   - Install dependencies
   - ESLint
   - TypeScript checking
   - Build verification

3. **Sync & Deploy** (main branch only)
   - Sync `/app/` to `/api/`
   - Validate sync integrity
   - Build Docker images
   - Deploy to production

## Environment Variables

### Required Secrets (GitHub)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=your_jwt_secret
JWT_AUDIENCE=authenticated
GPT_API_KEY=your_gpt_api_key
DEFAULT_USER_ID=your_default_user_id
FRONTEND_URL=https://your-frontend-domain.com
```

### Local Development (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=dev-secret-key
JWT_AUDIENCE=authenticated
GPT_API_KEY=dev-gpt-key
DEFAULT_USER_ID=your_user_id
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### Sync Issues
```bash
# Check what changed
python scripts/validate_sync.py

# Force re-sync
rm -rf api/
mkdir api/
python scripts/sync_to_production.py
```

### Deployment Issues
```bash
# Check Docker logs
docker-compose logs api
docker-compose logs web

# Rebuild from scratch
docker-compose down
docker system prune -f
docker-compose up --build
```

### Development Issues
```bash
# Reset development environment
git checkout develop
git reset --hard origin/develop
rm -rf __pycache__ .pytest_cache
pip install -r app/requirements.txt
```

## Best Practices

1. **Always develop in `/app/`** - Keep it clean for AI assistance
2. **Test sync before major releases** - Run validation scripts
3. **Use feature branches** - No direct commits to main/develop
4. **Write tests** - Both backend (pytest) and frontend (jest/vitest)
5. **Document breaking changes** - Update this guide when architecture changes