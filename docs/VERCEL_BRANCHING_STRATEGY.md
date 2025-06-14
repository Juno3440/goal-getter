# Vercel Branching Strategy for AI Development

## 🎯 **The Perfect AI Development Flow**

```
main (Production)     →  goal-getter.com
develop (Staging)     →  goal-getter-git-develop.vercel.app  
ai-dev (AI Branch)    →  goal-getter-git-ai-dev.vercel.app
feature/* (Features)  →  goal-getter-git-feature-*.vercel.app
```

---

## 🌳 **Branch Strategy**

### **🏗️ main → Production**
- **Purpose**: Live production app
- **Deployment**: Automatic to custom domain
- **Protection**: Require PR approval
- **Testing**: Full test suite + manual approval

### **🚀 develop → Staging** 
- **Purpose**: Integration testing
- **Deployment**: Auto-deploy to preview URL
- **Testing**: Automated tests + integration checks
- **Merges**: Collect features before production

### **🤖 ai-dev → AI Development**
- **Purpose**: AI-driven feature development  
- **Deployment**: Auto-deploy to AI preview URL
- **Usage**: AI makes changes here, user tests & approves
- **Fast iteration**: Skip heavy testing for speed

### **✨ feature/* → Feature Branches**
- **Purpose**: Specific feature development
- **Deployment**: Auto-deploy to feature preview URLs
- **Temporary**: Delete after merge

---

## 🔄 **AI Development Workflow**

### **AI Workflow:**
```bash
1. AI works on: ai-dev branch
2. AI pushes changes → Vercel deploys preview
3. User tests: goal-getter-git-ai-dev.vercel.app
4. User approves → AI merges ai-dev → develop
5. Staging tests pass → Manual promote develop → main
```

### **User Approval Process:**
```bash
# AI creates changes
git checkout ai-dev
# ... AI makes changes ...
git push origin ai-dev

# Vercel auto-deploys preview
# → goal-getter-git-ai-dev.vercel.app

# User tests & approves
# AI merges to staging
git checkout develop
git merge ai-dev
git push origin develop

# Staging tests pass
# Manual promotion to production
```

---

## ⚙️ **Vercel Configuration**

### **Environment Variables by Branch:**

```bash
# Production (main)
NEXT_PUBLIC_ENV=production
DATABASE_URL=postgres://prod-db-url
API_BASE_URL=https://goal-getter.com

# Staging (develop)  
NEXT_PUBLIC_ENV=staging
DATABASE_URL=postgres://staging-db-url
API_BASE_URL=https://goal-getter-git-develop.vercel.app

# AI Development (ai-dev)
NEXT_PUBLIC_ENV=development
DATABASE_URL=postgres://dev-db-url  
API_BASE_URL=https://goal-getter-git-ai-dev.vercel.app
```

### **vercel.json Configuration:**
```json
{
  "builds": [
    {
      "src": "web/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/requirements.txt", 
      "use": "@vercel/python"
    }
  ],
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.11"
    }
  },
  "github": {
    "autoDeploymentEnabled": true,
    "autoJobCancellation": true
  }
}
```

---

## 🛠️ **Vercel MCP Integration**

### **1. Deploy Official Vercel MCP:**
```bash
# Use Vercel's official template
npx create-next-app --example https://github.com/vercel-labs/mcp-on-vercel

# Or deploy directly
vercel deploy --env REDIS_URL=your-redis-url
```

### **2. Install Community MCP:**
```bash
# For comprehensive Vercel management
npm install -g nganiet/mcp-vercel

# Configure in Cursor/Claude
{
  "mcpServers": {
    "vercel": {
      "url": "https://your-mcp-server.vercel.app/api/mcp"
    }
  }
}
```

---

## 🎯 **Branch Protection Rules**

### **main (Production):**
- ✅ Require PR approval
- ✅ Require status checks (CI/CD)
- ✅ Require linear history
- ✅ Include administrators

### **develop (Staging):**
- ✅ Require status checks
- ✅ Auto-merge when checks pass
- ✅ Delete head branches

### **ai-dev (AI Development):**
- ✅ Allow force pushes (AI needs flexibility)
- ✅ Basic status checks only
- ❌ No approval required (speed over safety)

---

## 🚀 **Deployment Flow**

### **Automatic Deployments:**
```bash
ai-dev    → Always deploy (fast feedback)
develop   → Deploy + run integration tests  
main      → Deploy + full test suite + monitoring
feature/* → Deploy preview only
```

### **Manual Promotion:**
```bash
# Only main requires manual promotion
develop → main: Manual approval required
```

---

## 📊 **Monitoring & Observability**

### **Branch-Specific Monitoring:**
- **Production**: Full monitoring, alerts, analytics
- **Staging**: Integration testing, performance checks
- **AI-Dev**: Basic health checks, error tracking
- **Features**: Minimal monitoring

### **Vercel Analytics by Environment:**
```bash
Production: Full analytics + conversion tracking
Staging: Performance monitoring  
AI-Dev: Error tracking only
```

---

## 🎉 **Why This Strategy Works:**

### **✅ Benefits:**
- **Fast AI iteration** on `ai-dev`
- **Safe production** with `main` protection
- **Integration testing** with `develop` staging
- **Preview URLs** for every branch
- **Environment parity** across branches

### **🔄 Perfect for User-in-Loop:**
1. **AI develops** → `ai-dev` branch
2. **User tests** → Preview URL
3. **User approves** → Merge to `develop`
4. **Staging validates** → Auto-deploy
5. **Manual promote** → Production

---

## 🛠️ **Next Steps:**

1. **Set up Vercel project** with GitHub integration
2. **Configure branch protection** rules
3. **Install Vercel MCP** for AI management
4. **Create environment variables** per branch
5. **Test the workflow** with a simple change

This gives you the **perfect AI development environment** with Vercel! 🚀 