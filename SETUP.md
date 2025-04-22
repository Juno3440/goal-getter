# GoalGPT Setup Guide

This guide walks you through setting up the GoalGPT application with Supabase and deploying to Vercel.

## Supabase Setup

1. Create a Supabase account at https://supabase.com

2. Create a new Supabase project:
   - Choose a strong database password
   - Select a region close to your user base

3. Install the Supabase CLI and link your project:
   ```bash
   npm install -g supabase
   supabase login                             # authenticate with your Supabase account
   cd /path/to/GoalGPT
   supabase init                              # creates the supabase/ folder
   supabase link --project-ref <your-project-ref>  # link to your Supabase project
   ```

4. Deploy the database schema:
   ```
   supabase db push
   ```

5. Get your Supabase credentials:
   - From your Supabase project dashboard, go to Project Settings > API
   - Copy the URL and service_role_key
   - Also copy the anon key for the frontend

## Environment Variables

1. Backend (.env):
   - Copy and configure the example file:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and set:
     ```env
     SUPABASE_URL=https://your-project.supabase.co
     SUPABASE_KEY=your-service-role-key
     JWT_SECRET=your-secure-jwt-secret
     FRONTEND_URL=http://localhost:3000       # or your deployed frontend URL
     GPT_API_KEY=your-custom-api-key-for-gpt
     DEFAULT_USER_ID=your-default-user-id-for-development
     ```

2. Frontend (web/.env):
   - Copy and configure the example file:
     ```bash
     cd web
     cp .env.example .env
     ```
   - Edit `web/.env` and set:
     ```env
     VITE_SUPABASE_URL=https://your-project.supabase.co
     VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
     VITE_API_URL=http://localhost:8000       # or your deployed API URL
     ```

## Vercel Deployment

1. Create a Vercel account if you don't have one: https://vercel.com

2. Install the Vercel CLI:
   ```
   npm install -g vercel
   ```

3. Login to Vercel:
   ```
   vercel login
   ```

4. Deploy the project:
   ```
   vercel
   ```
   - Follow the prompts to link to your Vercel account and project
   
5. Configure environment variables in the Vercel dashboard:
   - Go to your project settings
   - Add the environment variables from the .env file

## Custom GPT Setup

1. Create a custom GPT in ChatGPT
   - Name: "Goal Manager"
   - Description: "Manage your hierarchical goals"
   
2. Configure API access:
   - Use the OpenAPI spec from your deployed API
   - Set up authentication using the GPT_API_KEY

3. Test the integration by asking the GPT to:
   - "Show my goals"
   - "Create a new goal to learn React"
   - "Mark my goal as done"

## Running with Docker Compose (optional)

To quickly start both backend and frontend locally via Docker Compose:

1. Ensure your root `.env` and `web/.env` are configured as described above.
2. From the project root, run:
   ```bash
   docker-compose up --build
   ```
3. Open your browser at http://localhost:3000
