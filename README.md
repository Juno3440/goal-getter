# Goal OS

**Goal OS** is a comprehensive goal tracking and management system designed to help you organize, track, and achieve your personal and professional objectives through a hierarchical structure.

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

## 🏗️ Architecture

Goal OS consists of two main components:

1. **Backend API** (`/api`): FastAPI-based REST API with Supabase integration
2. **Frontend Web App** (`/web`): React + TypeScript application with modern UI

## 🚀 Features

- **Hierarchical Goal Structure**: Organize goals in a tree-like structure with parent-child relationships
- **Real-time Updates**: Live synchronization across all connected clients
- **Progress Tracking**: Visual indicators and completion percentages
- **User Authentication**: Secure user management with JWT tokens
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Supabase**: Backend-as-a-Service for database and authentication
- **PostgreSQL**: Robust relational database
- **JWT**: Secure authentication tokens
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern UI library with hooks
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Supabase Client**: Real-time database integration
- **CSS Modules**: Scoped styling

### Development & Deployment
- **uv**: Fast Python package manager
- **pytest**: Testing framework
- **Black**: Code formatting
- **ESLint**: JavaScript/TypeScript linting
- **Vercel**: Deployment platform
- **GitHub Actions**: CI/CD pipeline

## 🎯 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- uv (Python package manager)
- Supabase account

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd goal-os
   ```

2. **Install backend dependencies**
   ```bash
   cd api
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Run the backend**
   ```bash
   uv run uvicorn main:app --reload
   ```

### Frontend Setup

1. **Install frontend dependencies**
   ```bash
   cd web
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Run the frontend**
   ```bash
   npm run dev
   ```

## 🧪 Testing

### Backend Tests
```bash
cd api
uv run pytest
```

### Frontend Tests
```bash
cd web
npm test
```

## 📁 Project Structure

```
Goal OS/
├── api/                    # Backend API
│   ├── main.py            # FastAPI application
│   ├── db.py              # Database operations
│   ├── tests/             # Backend tests
│   └── pyproject.toml     # Python dependencies
├── web/                   # Frontend application
│   ├── src/               # Source code
│   ├── tests/             # Frontend tests
│   └── package.json       # Node.js dependencies
├── docs/                  # Documentation
├── supabase/             # Database schema and config
└── vercel.json           # Deployment configuration
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