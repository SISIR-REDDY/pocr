# Railway Deployment Troubleshooting Guide

## Common Railway Deployment Errors & Solutions

### Error 1: "No start command detected"

**Solution:** Railway needs to know how to start your app.

**Fix:** Create `Procfile` in `backend/` directory:
```
web: python main.py
```

Or set in Railway dashboard:
- Go to Settings → Deploy
- Start Command: `python main.py`

---

### Error 2: "Module not found" or "Import error"

**Solution:** Dependencies not installed.

**Fix:** Ensure `requirements.txt` is in `backend/` directory and Railway detects it automatically.

**Verify:**
1. Check `backend/requirements.txt` exists
2. Railway should auto-detect and install dependencies
3. Check build logs for installation errors

---

### Error 3: "Root directory not found"

**Solution:** Railway is looking in wrong directory.

**Fix:** Set root directory in Railway:
1. Go to Settings → Source
2. Root Directory: `backend`
3. Save and redeploy

---

### Error 4: "Port already in use" or "Cannot bind to port"

**Solution:** Railway assigns port via environment variable.

**Fix:** Update `main.py` to use Railway's PORT:
```python
port = int(os.getenv("PORT", 8000))
```

✅ **Already done in your code!** Your `main.py` already uses `PORT` env var.

---

### Error 5: "Build failed" or "Installation failed"

**Possible causes:**
- Missing dependencies in requirements.txt
- Python version mismatch
- Large dependencies timeout

**Solutions:**
1. Check `requirements.txt` has all dependencies
2. Add Python version specification
3. Check build logs for specific error

---

### Error 6: "Repository not found" or "Access denied"

**Solution:** Railway needs GitHub access.

**Fix:**
1. Go to Railway dashboard → Settings → Connections
2. Reconnect GitHub
3. Authorize Railway to access your repository
4. Try deploying again

---

### Error 7: "Deployment timeout"

**Solution:** First deployment takes time (installing dependencies).

**Fix:**
- Wait 15-20 minutes for first deployment
- Check build logs to see progress
- If stuck, cancel and redeploy

---

## Step-by-Step Railway Setup (Fixed)

### Method 1: Deploy from GitHub (Recommended)

1. **Connect GitHub:**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - If repo not listed, click "Configure GitHub App"
   - Authorize Railway to access repositories
   - Select "All repositories" or specific repo

2. **Select Repository:**
   - Choose your `pocr` repository
   - Click "Deploy Now"

3. **Configure Service:**
   - Go to Settings → Source
   - Root Directory: `backend`
   - Save

4. **Set Start Command:**
   - Go to Settings → Deploy
   - Start Command: `python main.py`
   - Save

5. **Deploy:**
   - Railway will auto-detect Python
   - Install dependencies from `requirements.txt`
   - Start your app

---

### Method 2: Deploy with Railway CLI (Alternative)

If GitHub deployment fails, use CLI:

1. **Install Railway CLI:**
   ```bash
   # Windows (PowerShell)
   iwr https://railway.app/install.ps1 | iex
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize:**
   ```bash
   cd backend
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

---

### Method 3: Deploy from Local Files (If GitHub fails)

1. **Install Railway CLI** (see above)

2. **Login:**
   ```bash
   railway login
   ```

3. **Create Project:**
   ```bash
   railway init
   ```

4. **Link to Project:**
   ```bash
   railway link
   ```

5. **Deploy:**
   ```bash
   cd backend
   railway up
   ```

---

## Quick Fixes Checklist

- [ ] Root Directory set to `backend` in Railway settings
- [ ] Start Command set to `python main.py`
- [ ] `requirements.txt` exists in `backend/` directory
- [ ] GitHub repository is connected/authorized
- [ ] Python version is compatible (3.10+)
- [ ] Check build logs for specific errors

---

## Railway Configuration Files

### Option 1: Use Railway Dashboard (Easiest)
- Set Root Directory: `backend`
- Set Start Command: `python main.py`
- Railway auto-detects Python

### Option 2: Create `railway.json` (Optional)
Create `railway.json` in project root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && python main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Option 3: Create `Procfile` (Alternative)
Create `backend/Procfile`:
```
web: python main.py
```

---

## Check Build Logs

1. Go to Railway dashboard
2. Select your service
3. Click "Deployments" tab
4. Click on latest deployment
5. Check "Build Logs" and "Deploy Logs"
6. Look for specific error messages

---

## Common Error Messages & Fixes

| Error | Fix |
|-------|-----|
| "No start command" | Set Start Command: `python main.py` |
| "Module not found" | Check `requirements.txt` has all deps |
| "Root directory not found" | Set Root Directory: `backend` |
| "Port already in use" | Already handled in code (uses PORT env var) |
| "Build timeout" | Wait longer, first build takes 15-20 min |
| "GitHub access denied" | Reconnect GitHub in Railway settings |

---

## Alternative: Use Render Instead

If Railway continues to have issues, try **Render** (similar, often more reliable):

1. Go to https://render.com
2. Sign up (free)
3. New Web Service → Connect GitHub
4. Root Directory: `backend`
5. Build: `pip install -r requirements.txt`
6. Start: `python main.py`
7. Deploy

Render is often more reliable for Python deployments.

---

## Still Having Issues?

1. **Check Railway Status:** https://status.railway.app
2. **Check Build Logs:** Look for specific error messages
3. **Try Render:** Often more reliable for Python
4. **Use Railway CLI:** Alternative deployment method
5. **Check GitHub Connection:** Reconnect in Railway settings

---

## Quick Test: Verify Your Setup

Run locally to ensure everything works:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py
```

If this works locally, Railway should work too (once configured correctly).

