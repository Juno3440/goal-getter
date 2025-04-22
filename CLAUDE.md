# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build Commands
- Run server: `uvicorn app.main:app --reload`
- Run tests: `pytest`
- Check types: `mypy app/`
- Lint code: `flake8 app/`

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