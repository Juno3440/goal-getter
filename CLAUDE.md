# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture: Simplified Single API
- **`/api/`** - Single API codebase (all endpoints and features)
- **`/web/`** - Frontend React application
- **`/api/tests/`** - Backend tests

## Development Commands
- Run server: `cd api && python -m uvicorn main:app --reload --port 8000`
- Run tests: `cd api && pytest`
- Check types: `cd api && mypy .`
- Lint code: `cd api && flake8 .`

## Frontend Commands (in /web/)
- Run dev server: `npm run dev`
- Build: `npm run build`
- Lint: `npm run lint`
- Type check: `npm run type-check`

## Code Style Guide
- Follow PEP 8 conventions
- Sort imports: standard, third-party, local
- Use type annotations everywhere
- Models: Use Pydantic BaseModel
- API routes: Use FastAPI decorators with response models
- Error handling: Raise HTTPException with appropriate status codes
- File naming: snake_case
- Function naming: snake_case
- Class naming: PascalCase
- Variable naming: snake_case
- Document all public functions and modules with docstrings

## API Endpoints
- **GET /goals** - List all goals (hierarchical)
- **GET /api/tree** - Tree visualization format
- **POST /goals** - Create new goal
- **PATCH /goals/{id}** - Update goal
- **DELETE /goals/{id}** - Delete goal
- **GET /gpt/goals** - GPT integration endpoint (API key auth)

## CI/CD Pipeline
- **Trigger**: Push to `main` or `develop`, PRs to these branches
- **Backend Tests**: Python 3.11, flake8, mypy, pytest
- **Frontend Tests**: Node.js 18, ESLint, TypeScript, build verification
- **Deployment**: Direct deployment from `/api/`
- **Secrets Required**: `SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET`, `JWT_AUDIENCE`, `GPT_API_KEY`, `DEFAULT_USER_ID`, `FRONTEND_URL`

## Environment Variables
### Backend (.env)
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=your_jwt_secret
JWT_AUDIENCE=authenticated
GPT_API_KEY=your_gpt_api_key
DEFAULT_USER_ID=your_user_id
FRONTEND_URL=http://localhost:3000
```

### Frontend (web/.env)
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

## Deployment Options
### Option 1: Vercel (Recommended for MVP)
- **Setup**: Configure environment variables in Vercel dashboard
- **Deploy**: `git push origin main` (auto-deploys via GitHub integration)
- **Cost**: $0-$20/month, **Complexity**: Low

### Option 2: Docker (Self-hosted)
- **Setup**: `docker-compose up --build`
- **Deploy**: Use CI/CD to push to container registry
- **Cost**: $20-$100/month, **Complexity**: Medium

### Option 3: Railway/Render (Balanced)
- **Setup**: Connect GitHub repo, configure environment
- **Deploy**: Auto-deploy on push
- **Cost**: $20-$50/month, **Complexity**: Low-Medium

## Important Notes
- ALWAYS work in `/app/` for backend development
- NEVER edit `/api/` directly - it's auto-generated
- Run sync scripts before deployment
- Use feature branches for all development
- Test deployment with `python3 scripts/validate_sync.py`