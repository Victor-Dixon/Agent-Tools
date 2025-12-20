# 🔧 GitHub CLI Authentication Fix

**Problem**: `GH_TOKEN` environment variable is set with an invalid token, blocking `gh auth login`.

---

## 🚨 **QUICK FIX**

### **Step 1: Clear GH_TOKEN Environment Variable**

**PowerShell:**
```powershell
$env:GH_TOKEN = $null
Remove-Item Env:\GH_TOKEN -ErrorAction SilentlyContinue
```

**Or manually:**
1. Open System Properties → Environment Variables
2. Find `GH_TOKEN` in User or System variables
3. Delete it or set it to empty

### **Step 2: Run GitHub CLI Login**

```bash
gh auth login
```

**When prompted:**
1. **Where do you use GitHub?** → Select `GitHub.com`
2. **What account do you want to log into?** → Select your account
3. **What is your preferred protocol?** → Select `HTTPS` (recommended)
4. **Authenticate Git credential helper?** → Select `Yes`
5. **How would you like to authenticate?** → Select `Login with a web browser`
6. **Copy the code** and press Enter
7. **Authorize in your browser** when it opens

### **Step 3: Verify Authentication**

```bash
gh auth status
```

You should see:
```
github.com
  ✓ Logged in to github.com as <your-username>
  ✓ Git operations for github.com configured to use HTTPS
  ✓ Token: gho_...
```

---

## 🔍 **WHY THIS HAPPENED**

The `GH_TOKEN` environment variable was set with an invalid or expired token. GitHub CLI prioritizes this environment variable over stored credentials, so even if you try to log in, it uses the invalid token.

---

## ✅ **AFTER FIXING**

Once authenticated, you can:
- ✅ Create PRs using `gh pr create`
- ✅ Merge PRs using `gh pr merge`
- ✅ Use all GitHub CLI commands
- ✅ Use the unified PR tools without authentication errors

---

## 🐝 **WE. ARE. SWARM. ⚡🔥**

**Run the fix script or manually clear GH_TOKEN, then run `gh auth login`!**

