# Screenshot Workflow Setup Guide

This guide explains how to set up the human-in-the-loop screenshot approval workflow for frontend releases.

## 🔧 **Required GitHub Secrets**

Add these secrets to your GitHub repository (`Settings > Secrets and Variables > Actions`):

```bash
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id  
VERCEL_PROJECT_ID=your_project_id
```

### **Getting Vercel Credentials:**

1. **Vercel Token**: Go to [Vercel Account Settings](https://vercel.com/account/tokens) → Create new token
2. **Org ID & Project ID**: Run `vercel link` in your project, then check `.vercel/project.json`

## 🌍 **GitHub Environments Setup** (For Approach 2)

1. Go to `Settings > Environments` in your GitHub repo
2. Create two environments:
   - **staging** (no protection rules)
   - **production** (enable "Required reviewers" - add yourself)

## 📱 **Workflow Process**

### **When You Push Frontend Changes:**

1. **Automatic Testing**: ESLint, TypeScript, Jest tests run
2. **Preview Deployment**: Vercel creates preview URL
3. **Issue Created**: GitHub creates issue with testing checklist
4. **Your Action Required**:
   - 🔗 **Open preview URL**
   - 📱 **Test on desktop, mobile, tablet**
   - 📷 **Take screenshots of**:
     - Main pages/features
     - Mobile responsive design
     - Error states
     - Loading states
   - 📝 **Paste screenshots** in issue comments
   - ✅ **Comment "approved"** when satisfied

5. **Production Deploy**: Workflow continues automatically

## 📋 **Screenshot Checklist Template**

Use this checklist when reviewing:

```markdown
### 📷 Screenshots Taken:
- [ ] Desktop view (1920x1080)
- [ ] Mobile view (375x812)
- [ ] Tablet view (768x1024)
- [ ] New features in action
- [ ] Error states
- [ ] Loading states

### 🧪 Functionality Tested:
- [ ] Navigation works
- [ ] Forms submit correctly
- [ ] No console errors
- [ ] Responsive design
- [ ] Keyboard navigation
- [ ] Performance feels good

### ✅ Approval:
Screenshots uploaded ↑
**approved** 
```

## 🔄 **Integration with Existing Workflow**

This workflow integrates with your existing FEEDBACK_LOOP.md process:

1. **Replaces manual "user review" step** with automated GitHub issue
2. **Enforces screenshot documentation** before production
3. **Creates audit trail** of all UI changes
4. **Enables async approval** (no need to be online during deployment)

## ⚡ **Quick Commands**

```bash
# Test the workflow
git checkout -b feature/test-screenshots
# Make some frontend changes
git add . && git commit -m "feat(frontend): test screenshot workflow"
git push origin feature/test-screenshots

# Watch for GitHub issue creation
# Take screenshots and approve!
```

## 🚨 **Troubleshooting**

### **Issue: No GitHub issue created**
- Check `permissions: issues: write` in workflow
- Verify `GITHUB_TOKEN` has sufficient permissions

### **Issue: Vercel deployment fails**
- Verify all `VERCEL_*` secrets are correct
- Check Vercel project has correct framework settings

### **Issue: Timeout waiting for approval**
- Default timeout is 60 minutes
- Adjust `timeout-minutes` if needed
- Consider setting up Slack/email notifications

## 🎯 **Benefits**

✅ **No more missed screenshot reviews**  
✅ **Automated preview deployment**  
✅ **Audit trail of all UI changes**  
✅ **Async workflow** (review when convenient)  
✅ **Integration with existing tools**  
✅ **Zero infrastructure setup** 