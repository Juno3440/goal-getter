# GoalGPT

A modern goal tracking application with hierarchical goal management, designed for GPT integration.

## 🏗️ Architecture

- **`/api/`** - FastAPI backend with all endpoints
- **`/web/`** - React frontend with TypeScript
- **`/api/tests/`** - Backend test suite

## 🚀 Quick Start

### Backend
```bash
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd web
npm install
npm run dev
```

## 📋 Environment Setup

### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
JWT_SECRET=your_jwt_secret
JWT_AUDIENCE=authenticated
GPT_API_KEY=your_gpt_api_key
DEFAULT_USER_ID=your_user_id
FRONTEND_URL=http://localhost:3000
```

### Frontend (web/.env)
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

## 🔧 Development

### Backend Commands
```bash
cd api
python -m uvicorn main:app --reload  # Start server
pytest                               # Run tests
mypy .                              # Type checking
flake8 .                            # Linting
```

### Frontend Commands
```bash
cd web
npm run dev         # Start dev server
npm run build       # Build for production
npm run lint        # ESLint
npm run type-check  # TypeScript checking
npm test           # Run tests
```

## 🌐 API Endpoints

- **GET /goals** - List all goals (hierarchical)
- **GET /api/tree** - Tree visualization format
- **POST /goals** - Create new goal
- **PATCH /goals/{id}** - Update goal
- **DELETE /goals/{id}** - Delete goal
- **GET /gpt/goals** - GPT integration endpoint (API key auth)

## 🤖 GPT Integration

The API includes endpoints designed for GPT/AI tool calling:
- JWT authentication for user-specific goals
- API key authentication for AI agents
- Tree visualization endpoint for frontend rendering

## 🚢 Deployment

The application is configured for easy deployment to Vercel or similar platforms. All environment variables need to be configured in your deployment environment.

## 📁 Project Structure

```
GoalGPT/
├── api/                 # Backend API
│   ├── main.py         # FastAPI application
│   ├── db.py           # Database operations
│   ├── requirements.txt # Python dependencies
│   └── tests/          # Backend tests
├── web/                # Frontend React app
│   ├── src/            # React source code
│   ├── package.json    # Node dependencies
│   └── ...
└── .github/workflows/  # CI/CD pipeline
```

## Features

- Hierarchical goal management with tree visualization
- User authentication via Supabase
- Direct GPT integration through tool-calling
- Responsive web UI built with React, Tailwind CSS, and D3.js
- Database persistence with PostgreSQL (via Supabase)

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- A Supabase account
- Vercel account (for deployment)

### Local Development

1. Clone the repository
   ```
   git clone https://github.com/yourusername/GoalGPT.git
   cd GoalGPT
   ```

2. Create Supabase project and set up the database
   ```
   npm install -g supabase
   supabase login
   supabase init
   supabase db push
   ```

3. Create `.env` file with your Supabase credentials
   ```
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Setup frontend environment
   ```
   cd web
   cp .env.example .env
   # Edit .env with your credentials
   npm install
   ```

5. Run the backend (using uv)
   ```bash
   uv venv
   uv pip install -r api/requirements.txt "uvicorn[standard]" supabase python-dotenv
   uv run -- uvicorn api.main:app --reload --env-file .env
   ```

6. Run the frontend
   ```
   cd web
   npm run dev
   ```

7. Open your browser at http://localhost:3000

### Running with Docker Compose

Alternatively, you can start both the backend and frontend via Docker Compose:

1. Copy and configure environment files in the project root:
   ```bash
   cp .env.example .env
   # Edit .env to set SUPABASE_URL, SUPABASE_KEY, JWT_SECRET, GPT_API_KEY, DEFAULT_USER_ID, FRONTEND_URL
   cp web/.env.example web/.env
   # Edit web/.env to set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
   ```
2. Build and run services:
   ```bash
   docker-compose up --build
   ```
3. Open your browser at http://localhost:3000

## Deployment

### Vercel Deployment

This project is optimized for Vercel deployment. See [SETUP.md](SETUP.md) for detailed instructions.

## Architecture

- **Backend**: FastAPI + Supabase
- **Frontend**: React + Tailwind CSS + D3.js
- **Database**: PostgreSQL (managed by Supabase)
- **Authentication**: Supabase Auth
- **AI Integration**: GPT native tool-calling

## GPT Integration

See [docs/gpt-setup.md](docs/gpt-setup.md) for instructions on setting up the custom GPT with this API.

## License

MIT