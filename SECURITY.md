# Security Guidelines

## Environment Variables

**⚠️ NEVER commit secrets to the repository!**

This project uses environment variables for sensitive configuration. All secrets should be stored in `.env` files that are excluded from version control.

### Required Environment Variables

For the API to function, you need these environment variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# JWT Configuration (for testing)
JWT_SECRET=your-secret-key-for-development
JWT_AUDIENCE=authenticated
```

### Setting Up Environment Variables

1. **For Development:**
   ```bash
   cd api
   bash setup_test_env.sh
   # Then edit the generated .env file with your actual credentials
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
**Issue:** Supabase service key was accidentally committed to the repository  
**Resolution:** 
- Removed hardcoded secrets from `api/tests/conftest.py`
- Updated code to use environment variables
- Added this security documentation

**Action Items:**
- [ ] Rotate the exposed Supabase key if it was sensitive
- [ ] Review all commits for other potential secrets
- [ ] Set up pre-commit hooks to prevent secret commits in the future

## Best Practices

1. **Never hardcode secrets** in source code
2. **Use environment variables** for all sensitive configuration
3. **Keep .env files local** and never commit them
4. **Use separate credentials** for development, testing, and production
5. **Rotate secrets regularly** especially if they may have been exposed
6. **Use read-only keys** when possible (e.g., anon keys vs service keys)

## Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** create a public issue
2. Email the maintainers directly
3. Include steps to reproduce and potential impact
4. We will respond within 48 hours 