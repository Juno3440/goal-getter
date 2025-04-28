# GPT GoalGraph

A lightweight, AI-native goal management system with Supabase and GPT integration.

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