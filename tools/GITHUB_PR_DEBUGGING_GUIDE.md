# 🔧 GitHub PR Debugging Guide

**Status**: ✅ **DEBUGGER CREATED** - Use `github_pr_debugger.py` to diagnose PR issues

---

## 🚨 **COMMON PR PROBLEMS IDENTIFIED**

### **1. Broken Imports** ✅ **FIXED**
- **Issue**: `unified_github_pr_creator.py` had broken import syntax
- **Fix**: Replaced with SSOT imports from `src.core.utils.github_utils`
- **Status**: ✅ Fixed

### **2. Missing TimeoutConstants** ✅ **FIXED**
- **Issue**: Multiple files missing `TimeoutConstants` import
- **Fix**: Added imports with fallback values
- **Files Fixed**:
  - `unified_github_pr_creator.py`
  - `create_batch2_prs.py`
  - `resolve_pr_blockers.py`
- **Status**: ✅ Fixed

### **3. Inconsistent Token Retrieval** ✅ **FIXED**
- **Issue**: Multiple different ways to get GitHub token
- **Fix**: Standardized on SSOT `github_utils.get_github_token()`
- **Status**: ✅ Fixed

### **4. Rate Limit Handling** ⚠️ **NEEDS IMPROVEMENT**
- **Issue**: Rate limit checking tools archived
- **Fix**: Added inline rate limit checking functions
- **Status**: ✅ Fixed (temporary)

### **5. Authentication Issues** 🔍 **DEBUGGABLE**
- **Issue**: GitHub CLI auth not checked before PR creation
- **Fix**: Debugger now checks auth status
- **Status**: ✅ Debuggable

---

## 🛠️ **DEBUGGING TOOL**

### **Usage**:
```bash
# Diagnose PR creation issue
python tools/github_pr_debugger.py --repo Streamertools --head merge-MeTuber-20251124 --base main

# Generate fix script
python tools/github_pr_debugger.py --repo Streamertools --head merge-MeTuber-20251124 --base main --fix-script
```

### **What It Checks**:
1. ✅ GitHub CLI installation
2. ✅ GitHub CLI authentication
3. ✅ GitHub token availability
4. ✅ GitHub token validity
5. ✅ Rate limits (REST API, GraphQL, GitHub CLI)
6. ✅ Branch existence
7. ✅ PR already exists

### **Output**:
- Status report (healthy/degraded/blocked)
- List of issues found
- Fix recommendations
- Rate limit status
- Authentication status

---

## 🔧 **FIXES APPLIED**

### **1. unified_github_pr_creator.py**
- ✅ Fixed broken imports
- ✅ Added SSOT token retrieval
- ✅ Added inline rate limit checking
- ✅ Fixed TimeoutConstants import

### **2. create_batch2_prs.py**
- ✅ Fixed TimeoutConstants imports
- ✅ Standardized token retrieval
- ✅ Added fallback timeouts

### **3. resolve_pr_blockers.py**
- ✅ Fixed TimeoutConstants imports
- ✅ Added proper timeout handling

---

## 🚀 **HOW TO USE**

### **Step 1: Diagnose the Issue**
```bash
python tools/github_pr_debugger.py --repo <repo> --head <branch> --base <base>
```

### **Step 2: Review Diagnosis**
- Check status (healthy/degraded/blocked)
- Review issues found
- Check rate limits
- Verify authentication

### **Step 3: Apply Fixes**
- Follow fix recommendations
- Run `gh auth login` if needed
- Set `GITHUB_TOKEN` in `.env` if missing
- Wait for rate limit reset if needed

### **Step 4: Retry PR Creation**
```bash
python tools/unified_github_pr_creator.py <repo> <title> <head> <base> <body_file>
```

---

## 📋 **COMMON FIXES**

### **GitHub CLI Not Authenticated**
```bash
gh auth login
```

### **GitHub Token Missing**
```bash
# Add to .env file
GITHUB_TOKEN=your_token_here
```

### **Rate Limit Exceeded**
```bash
# Wait for reset or use GitHub CLI (different rate limit)
gh pr create --repo owner/repo --head branch --base main --title "Title" --body "Body"
```

### **Branch Not Found**
```bash
# Check branch name
git ls-remote --heads origin <branch>

# Or create branch
git checkout -b <branch>
git push origin <branch>
```

---

## ✅ **STATUS**

- ✅ **Debugger Created**: `github_pr_debugger.py`
- ✅ **Imports Fixed**: All GitHub PR tools
- ✅ **Token Retrieval**: Standardized on SSOT
- ✅ **Timeout Handling**: Fixed with fallbacks
- ✅ **Rate Limit Checking**: Added inline functions

---

## 🐝 **WE. ARE. SWARM. ⚡🔥**

**Use the debugger to identify and fix PR issues quickly!**

