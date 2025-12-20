# 🚀 Quick Fix GitHub PR Issues

## **ONE COMMAND FIX:**

```bash
python tools/fix_github_prs.py
```

**OR:**

```bash
python tools/github_pr_debugger.py --fix
```

---

## **What It Does:**

1. ✅ Clears `GH_TOKEN` environment variable (if set)
2. ✅ Checks GitHub CLI authentication
3. ✅ Checks GitHub token availability
4. ✅ Shows what needs to be fixed

---

## **If Not Authenticated:**

Run:
```bash
gh auth login
```

---

## **That's It!** 🐝⚡🔥

