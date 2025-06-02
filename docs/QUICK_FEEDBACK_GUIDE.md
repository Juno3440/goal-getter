# Quick Feedback Loop Guide

## 🎯 **The Essential AI Workflow**

This is the **practical, working feedback loop** for GoalGPT development.

---

## 🔄 **Step-by-Step Process**

### **1. Make Changes**
```bash
# Frontend changes
cd web/
npm run dev  # Test locally at http://localhost:5173

# Backend changes  
cd api/
uv run uvicorn main:app --reload  # Test locally at http://localhost:8000
```

### **2. Test Locally**
```bash
# Frontend
cd web/
npm run lint && npm run type-check && npm run test

# Backend
cd api/
uv run pytest && uv run mypy . && uv run flake8 .
```

### **3. Push & Monitor CI**
```bash
git add .
git commit -m "feat: describe your changes"
git push origin develop
```

### **4. AI Must Check CI Status**
```bash
# AI uses GitHub Actions MCP to:
# - Check workflow status
# - Get logs if failed
# - Fix issues and re-push
```

### **5. User Review (Frontend Only)**
- **AI**: "Changes pushed, CI passing. Please review at [preview URL]"
- **User**: Takes screenshots, provides feedback
- **AI**: Implements feedback, repeats loop

---

## 🤖 **AI Commands for Monitoring**

```javascript
// Check latest runs
mcp_github-actions_list_workflow_runs(owner: "Juno3440", repo: "goal-getter")

// Get specific run details
mcp_github-actions_get_workflow_run(runId: XXXXX)

// Get job details and logs
mcp_github-actions_get_workflow_run_jobs(runId: XXXXX)
```

---

## 📊 **Current Status**

### ✅ **Working:**
- Backend CI/CD (tests passing)
- Frontend CI/CD (TypeScript fixed!)
- GitHub Actions monitoring
- Vercel deployment config

### 🚧 **Next Steps:**
1. Wait for current CI to complete
2. Set up Vercel deployment
3. Test full feedback loop

---

## 🎯 **Success Criteria**

- **CI must pass** before asking for user review
- **User approval required** for frontend changes
- **Fix issues within 1-2 iterations**
- **Zero production bugs**

**The feedback loop is working! 🎉** 