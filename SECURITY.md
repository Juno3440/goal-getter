# Security Guidelines

## Environment Variables

**⚠️ NEVER commit secrets to the repository!**

This project uses environment variables for sensitive configuration. All secrets should be stored in `.env` files that are excluded from version control.

### Required Environment Variables

For the API to function, you need these environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here  # Anon key (safe for client-side use)

# JWT Configuration (for testing)
JWT_SECRET=your-secret-key-for-development
JWT_AUDIENCE=authenticated
```

### Supabase Key Types

**Anon Key** (Public):
- Safe to expose in client-side code
- Only has access to public data and respects Row Level Security (RLS)
- Used for client applications and development
- This is what we use in our development environment

**Service Key** (Private):
- Full admin access to your database
- Should NEVER be committed or exposed publicly
- Only used in secure server environments
- Not used in this project's development setup

### Setting Up Environment Variables

1. **For Development:**
   ```bash
   cd api
   bash setup_test_env.sh
   # This will create a .env file with current dev environment credentials
   ```

2. **For Testing:**
   ```bash
   # Set environment variables in your shell or CI/CD system
   export SUPABASE_URL="https://your-dev-project.supabase.co"
   export SUPABASE_KEY="your_dev_anon_key"
   export JWT_SECRET="your-test-secret"
   ```

3. **For Production:**
   Use your deployment platform's environment variable system (Vercel, Heroku, etc.)

## Security Incident: Committed Secrets

**Date:** 2025-01-02  
**Issue:** Supabase anon key was accidentally committed to the repository  
**Severity:** Low (anon keys are designed to be public-safe)  
**Resolution:** 
- Removed hardcoded secrets from all test files
- Updated code to use environment variables
- Added this security documentation
- Verified current anon key is still active and secure

**Analysis:**
The exposed key was a Supabase anon key, which is designed to be safe for client-side use. However, hardcoding any credentials is still a bad practice that we've now corrected.

**Action Items:**
- [x] Removed hardcoded secrets from codebase
- [x] Updated environment variable management
- [x] Added security documentation
- [ ] Set up pre-commit hooks to prevent secret commits in the future

## Best Practices

1. **Never hardcode secrets** in source code (even "safe" ones)
2. **Use environment variables** for all sensitive configuration
3. **Keep .env files local** and never commit them
4. **Use separate credentials** for development, testing, and production
5. **Understand key types** - know the difference between anon and service keys
6. **Use read-only keys** when possible (e.g., anon keys vs service keys)
7. **Rotate secrets regularly** especially if they may have been exposed

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** create a public issue
2. Email the maintainers directly
3. Include steps to reproduce and potential impact
4. We will respond within 48 hours 