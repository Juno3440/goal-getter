# Development Feedback Loops

This document defines the critical feedback loops for AI-assisted development in GoalGPT. These loops ensure tight synchronization between AI development, user validation, and automated testing.

## 🔄 **Core Philosophy**

The feedback loop is the **most important aspect** of AI development in this project. It ensures:
- **Rapid iteration** with immediate validation
- **User-centric development** through visual confirmation
- **Code quality** through automated testing
- **Deployment confidence** through CI/CD validation

---

## 🎨 **Frontend Feedback Loop**

### **Phase 1: Development & Local Testing**

1. **Make Changes**
   ```bash
   cd web/
   # Make your React component changes
   npm run dev  # Start development server
   ```

2. **Local Validation**
   ```bash
   npm run lint        # Fix linting issues
   npm run type-check  # Fix TypeScript errors
   npm run test        # Ensure tests pass
   ```

3. **Manual Review** ⭐ **HUMAN IN THE LOOP**
   - Open `http://localhost:5173`
   - **Take screenshots** of key functionality
   - **Test user interactions** manually
   - **Verify visual design** matches expectations

### **Phase 2: Push & CI Validation**

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   git push origin develop
   ```

5. **Monitor CI Pipeline** 🤖
   - Check: https://github.com/Juno3440/goal-getter/actions
   - **AI MUST**: Query workflow status using GitHub Actions MCP
   - **AI MUST**: Get logs if any step fails
   - **AI MUST**: Fix issues and re-push

### **Phase 3: Preview Deployment & User Review**

6. **Vercel Preview Deploy** (Automatic)
   - Vercel automatically deploys on push to `develop`
   - Get preview URL from Vercel dashboard or GitHub PR comments

7. **User Screenshot Review** ⭐ **HUMAN IN THE LOOP**
   - **User visits preview URL**
   - **User takes screenshots** of:
     - Main functionality working
     - Any visual issues
     - Mobile responsiveness
   - **User provides feedback** via GitHub issue or direct message

### **Phase 4: Production Release**

8. **Merge to Main** (After user approval)
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

---

## ⚙️ **Backend Feedback Loop**

### **Phase 1: Development & Testing**

1. **Make Changes**
   ```bash
   cd api/
   # Make your FastAPI changes
   uv run uvicorn main:app --reload  # Start development server
   ```

2. **Automated Testing** 🤖
   ```bash
   uv run pytest                    # Run all tests
   uv run pytest --cov=.          # Run with coverage
   uv run mypy .                   # Type checking
   uv run flake8 .                 # Linting
   ```

3. **API Testing**
   - Test endpoints with `curl` or Postman
   - Verify database operations
   - Check error handling

### **Phase 2: CI/CD Pipeline**

4. **Push & Validate**
   ```bash
   git push origin develop
   ```

5. **Monitor CI Results** 🤖
   - **AI MUST**: Check GitHub Actions status
   - **AI MUST**: Review test results and coverage
   - **AI MUST**: Fix any failing tests immediately

### **Phase 3: Integration Testing**

6. **Full Stack Testing**
   - Verify frontend can connect to backend API
   - Test authentication flows
   - Validate data persistence

---

## 🔍 **AI Workflow Monitoring Commands**

### **Essential AI Commands for Feedback Loop**

```bash
# 1. Check latest workflow status
# AI uses: mcp_github-actions_list_workflow_runs

# 2. Get specific run details  
# AI uses: mcp_github-actions_get_workflow_run

# 3. Get job logs for debugging
# AI uses: mcp_github-actions_get_workflow_run_jobs

# 4. Check current deployment status
# Check Vercel dashboard or GitHub deployments
```

### **AI Must Follow This Process:**

1. **After every code change**: Check CI status
2. **If CI fails**: Get logs, analyze, fix, re-push
3. **Before asking user for review**: Ensure CI passes
4. **After user feedback**: Implement changes and repeat loop

---

## 📸 **Screenshot Collection Workflow**

### **For Frontend Changes:**

1. **AI pushes changes** → Vercel deploys preview
2. **AI notifies user**: "Preview ready at [URL], please review and screenshot"
3. **User reviews** and takes screenshots of:
   - ✅ Working functionality
   - ❌ Any issues found
   - 📱 Mobile view (if applicable)
4. **User provides feedback** with screenshots
5. **AI implements fixes** based on feedback
6. **Repeat until user approves**

### **Screenshot Checklist:**
- [ ] Main page loads correctly
- [ ] Key user interactions work
- [ ] Visual design matches expectations  
- [ ] No console errors
- [ ] Mobile responsiveness (if applicable)

---

## 🚀 **Current Project Status**

### **Working:**
- ✅ Backend CI/CD (tests passing)
- ✅ Vercel deployment configuration
- ✅ GitHub Actions workflow

### **Needs Attention:**
- ❌ Frontend TypeScript errors (blocking CI)
- ⚠️ No active Vercel deployment yet
- ⚠️ Need to set up Vercel environment variables

### **Next Steps:**
1. Fix frontend TypeScript errors
2. Deploy to Vercel with proper environment variables
3. Test full feedback loop with real deployment

---

## 🎯 **Success Metrics**

- **CI Pipeline**: Must pass on every push
- **User Approval**: Required for all frontend changes
- **Response Time**: Fix issues within 1-2 iterations
- **Quality**: Zero production bugs through proper testing

**Remember**: The feedback loop is only as strong as its weakest link. AI must be disciplined about checking CI status and user must be engaged in the review process. 