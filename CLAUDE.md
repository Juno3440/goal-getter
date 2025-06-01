# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture: Development/Production Split
- **`/app/`** - Clean development API (work here for AI-assisted development)
- **`/api/`** - Production build (auto-generated, don't edit directly)
- Use `scripts/sync_to_production.py` before deployment
- See `docs/git-workflow.md` for complete workflow guide

## Development Commands
- Run server: `uvicorn app.main:app --reload`
- Run tests: `pytest app/`
- Check types: `mypy app/`
- Lint code: `flake8 app/`
- Sync to production: `python scripts/sync_to_production.py`
- Validate sync: `python scripts/validate_sync.py`

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

## CI/CD Pipeline
- **Trigger**: Push to `main` or `develop`, PRs to these branches
- **Backend Tests**: Python 3.11, flake8, mypy, pytest
- **Frontend Tests**: Node.js 18, ESLint, TypeScript, build verification
- **Deployment**: Auto-sync `/app/` → `/api/` and deploy on main branch
- **Secrets Required**: `SUPABASE_URL`, `SUPABASE_KEY`, `JWT_SECRET`, `JWT_AUDIENCE`, `GPT_API_KEY`, `DEFAULT_USER_ID`, `FRONTEND_URL`

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