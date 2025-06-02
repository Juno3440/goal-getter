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

# Supabase Configuration (get these from your Supabase dashboard)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# JWT Configuration
JWT_SECRET=your-secret-key-for-development
JWT_AUDIENCE=authenticated

# Optional: GPT Integration
GPT_API_KEY=your-gpt-api-key
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
EOF
    echo "Please edit the .env file with your actual Supabase credentials"
else
    echo ".env file already exists"
fi

echo "Setup complete!"
echo ""
echo "To run tests, make sure your .env file contains valid Supabase credentials"
echo "Then run: source .venv/bin/activate && python -m pytest" 