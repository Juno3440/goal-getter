#!/bin/bash
# Test Environment Setup Script
# Run this script to set up environment variables for testing

echo "Setting up test environment variables..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cat > .env << EOF
# GoalGPT API Environment Variables
# DO NOT COMMIT THIS FILE

# Supabase Configuration - DEV Environment
# These are current active credentials for the dev environment
SUPABASE_URL=https://tstnyxldiqfbcvzxtzxi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdG55eGxkaXFmYmN2enh0enhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4ODY5MTgsImV4cCI6MjA2NDQ2MjkxOH0.qinSNo9vUvAEQsrJcESBjmUnJWagJbSX0RguxjMr1C0

# JWT Configuration
JWT_SECRET=your-secret-key-for-development
JWT_AUDIENCE=authenticated

# Optional: GPT Integration
GPT_API_KEY=your-gpt-api-key
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
EOF
    echo "✅ Created .env file with current dev environment credentials"
    echo "   The Supabase credentials are ready to use for development/testing"
    echo "   You may want to update JWT_SECRET for additional security"
else
    echo "✅ .env file already exists"
fi

echo "Setup complete!"
echo ""
echo "Environment configured for goal-gpt-dev project (tstnyxldiqfbcvzxtzxi)"
echo "To run tests: source .venv/bin/activate && python -m pytest"
echo "To run API server: source .venv/bin/activate && uvicorn main:app --reload --port 8000" 