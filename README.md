# GoalGPT

A hierarchical goal management application with FastAPI backend and React frontend, designed for LLM integration and optimized for productivity workflows.

## 🚀 **Recent Migration to uv**

This project has been migrated from pip to **[uv](https://docs.astral.sh/uv/)** for faster, more reliable dependency management. 

### ✨ **Benefits of uv:**
- **10-100x faster** dependency resolution and installation
- **Deterministic builds** with `uv.lock` lockfile
- **Drop-in replacement** for pip with better error messages
- **Single tool** for dependency management, virtual environments, and Python version management

### 🔧 **Development Workflow with uv:**

```bash
# Install uv (if you haven't already)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Set up the project
uv sync --dev                    # Install all dependencies (including dev)
make run-dev                     # Start development server
make test                        # Run tests
make lint                        # Check code quality
make format                      # Format code

# Available make commands:
make help                        # Show all available commands
```

### 📦 **Key Files:**
- **`pyproject.toml`** - Project configuration, dependencies, and tool settings
- **`uv.lock`** - Lockfile ensuring reproducible builds (commit this!)
- **`Makefile`** - Development workflow shortcuts

---

## Architecture

**Frontend (React + TypeScript)**
- Vite build system
- TailwindCSS for styling  
- Tree visualization for goal hierarchies
- Real-time goal management interface

**Backend (FastAPI + Python)**
- RESTful API with automatic OpenAPI docs
- JWT authentication integration
- Supabase database integration
- Hierarchical goal tree management

**Deployment**
- **Vercel** for both frontend and backend deployment
- Environment-based configuration
- Automatic deployments from main branch

## Quick Start

### Prerequisites
- **uv** (recommended) or Python 3.10+
- **Node.js 18+** (for frontend)
- **Supabase account** (for database)

### Backend Setup

1. **Install dependencies:**
   ```bash
   uv sync --dev
   ```

2. **Environment setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

3. **Run development server:**
   ```bash
   make run-dev
   # or: uv run uvicorn api.main:app --reload
   ```

4. **API Documentation:** http://localhost:8000/docs

### Frontend Setup

1. **Navigate to web directory:**
   ```bash
   cd web
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Frontend:** http://localhost:3000

### Database Setup

1. Create a new Supabase project
2. Run the SQL migrations in `supabase/migrations/`
3. Configure Row Level Security (RLS) policies
4. Update environment variables

## Development Workflow

### Code Quality Tools (All configured in pyproject.toml)

```bash
make lint                        # Run all linting (flake8, black, isort, mypy)
make format                      # Auto-format code (black, isort)
make type-check                  # Type checking with mypy
make test                        # Run tests with coverage
```

### Pre-commit Hooks

```bash
make pre-commit                  # Install git hooks for automatic formatting
```

### Testing

```bash
make test                        # Run all tests with coverage
uv run pytest api/tests/         # Run specific test directory
uv run pytest -v -k "test_name"  # Run specific test
```

## Project Structure

```
GoalGPT/
├── api/                         # FastAPI backend
│   ├── main.py                  # FastAPI application
│   ├── db.py                    # Database operations
│   └── tests/                   # Backend tests
├── web/                         # React frontend
│   ├── src/                     # Frontend source
│   └── package.json             # Frontend dependencies
├── supabase/                    # Database migrations
├── .github/workflows/           # CI/CD pipelines
├── pyproject.toml              # Python project config & dependencies
├── uv.lock                     # Dependency lockfile
├── Makefile                    # Development commands
└── vercel.json                 # Deployment configuration
```

## API Endpoints

### Authentication
- All endpoints require JWT token in `Authorization: Bearer <token>` header
- Tokens obtained through Supabase Auth

### Goal Management
```bash
GET    /goals                    # List all user goals (hierarchical)
POST   /goals                    # Create new goal
GET    /goals/{id}               # Get specific goal with children
PATCH  /goals/{id}               # Update goal (title, status)
DELETE /goals/{id}               # Delete goal
GET    /api/tree                 # Get goals formatted for tree visualization
```

### Development/GPT Access
```bash
GET    /gpt/goals                # Simplified endpoint with API key auth
```

## Deployment

### Vercel Deployment (Recommended)

1. **Connect repository to Vercel**
2. **Set environment variables:**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   JWT_SECRET=your_jwt_secret
   GPT_API_KEY=your_gpt_api_key
   FRONTEND_URL=your_frontend_url
   ```

3. **Deploy:** Automatic on push to main branch

### Local Production Build

```bash
# Backend
uv build                         # Build Python package
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd web && npm run build          # Build React app
```

## Environment Variables

### Backend (.env)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
JWT_SECRET=your_jwt_secret
JWT_AUDIENCE=authenticated
GPT_API_KEY=your_openai_api_key
DEFAULT_USER_ID=optional_default_user
FRONTEND_URL=http://localhost:3000
```

### Frontend (web/.env)
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_URL=http://localhost:8000
```

## Contributing

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/your-feature`
3. **Make changes with proper testing**
4. **Ensure code quality:** `make lint && make test`
5. **Commit changes:** `git commit -m "Add your feature"`
6. **Push to branch:** `git push origin feature/your-feature`
7. **Create Pull Request**

### Code Standards
- **Python:** Follow PEP 8, use type hints
- **TypeScript:** Follow project ESLint configuration
- **Testing:** Maintain >70% coverage
- **Documentation:** Update README for significant changes

## Troubleshooting

### Common Issues

**uv command not found:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart your terminal
```

**Import errors:**
```bash
uv sync --dev                    # Reinstall dependencies
```

**Test failures:**
```bash
make clean                       # Clear caches
make test                        # Run tests again
```

**Frontend build issues:**
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

## License

MIT License - see LICENSE file for details.

---

**Built with:** FastAPI, React, TypeScript, Supabase, uv, Vercel