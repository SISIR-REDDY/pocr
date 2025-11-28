# Railway Deployment Quick Fix

## 🔧 Common Errors & Quick Fixes

### What error are you seeing?

**Please check Railway dashboard → Your Service → Deployments → Latest → Build Logs**

Common errors and fixes:

---

## Error: "No start command detected"

**Fix:** I've created `backend/Procfile` for you. 

**Manual fix:**
1. Go to Railway dashboard
2. Your service → Settings → Deploy
3. Start Command: `python main.py`
4. Save and redeploy

---

## Error: "Root directory not found" or "Cannot find main.py"

**Fix:** Set root directory to `backend`

1. Go to Railway dashboard
2. Your service → Settings → Source
3. Root Directory: `backend`
4. Save and redeploy

---

## Error: "Module not found" or "Import error"

**Fix:** Dependencies not installing

1. Check `backend/requirements.txt` exists ✅ (it does)
2. Railway should auto-detect and install
3. Check build logs for specific missing package
4. If issue persists, add to requirements.txt

---

## Error: "GitHub repository not found" or "Access denied"

**Fix:** Reconnect GitHub

1. Railway dashboard → Settings → Connections
2. Click "Configure GitHub App"
3. Authorize Railway
4. Select "All repositories" or your specific repo
5. Try deploying again

---

## Error: "Build timeout" or "Deployment failed"

**Fix:** First deployment takes 15-20 minutes

1. Wait patiently (installing dependencies)
2. Check build logs for progress
3. If stuck >30 min, cancel and try again
4. Or use Railway CLI (see below)

---

## 🚀 Alternative: Use Railway CLI (More Reliable)

If GitHub deployment keeps failing, use CLI:

### Step 1: Install Railway CLI
```powershell
# Windows PowerShell
iwr https://railway.app/install.ps1 | iex
```

### Step 2: Login
```bash
railway login
```
(Opens browser for authentication)

### Step 3: Initialize Project
```bash
cd backend
railway init
```
Follow prompts:
- Create new project? Yes
- Project name: (choose a name)

### Step 4: Deploy
```bash
railway up
```

This uploads your code directly (no GitHub needed!)

---

## 🎯 Recommended: Use Render Instead

If Railway continues to have issues, **Render is often more reliable** for Python:

### Render Deployment (5 minutes)

1. **Go to:** https://render.com
2. **Sign up** (free, with GitHub)
3. **New Web Service** → Connect GitHub
4. **Repository:** Select `pocr`
5. **Settings:**
   - **Name:** `optical-recognition-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
6. **Click "Create Web Service"**
7. **Wait 15-20 minutes** (first deployment)
8. **Copy your URL** (e.g., `https://your-app.onrender.com`)

**Render is often more reliable than Railway for Python apps!**

---

## ✅ Quick Checklist

Before deploying, verify:

- [ ] `backend/requirements.txt` exists ✅
- [ ] `backend/main.py` exists ✅
- [ ] Root Directory set to `backend` in Railway
- [ ] Start Command set to `python main.py` in Railway
- [ ] GitHub repository connected in Railway
- [ ] Check build logs for specific errors

---

## 🔍 How to Check Build Logs

1. Go to Railway dashboard
2. Select your service
3. Click "Deployments" tab
4. Click on latest deployment
5. Check "Build Logs" for errors
6. Check "Deploy Logs" for runtime errors

**Share the error message from logs and I can help fix it!**

---

## 📋 Step-by-Step Railway Setup (Fixed)

### Method 1: Dashboard (Try This First)

1. **Railway Dashboard:** https://railway.app/dashboard
2. **New Project** → **Deploy from GitHub repo**
3. **If repo not listed:**
   - Click "Configure GitHub App"
   - Authorize Railway
   - Select repositories
   - Try again
4. **Select repository:** `pocr`
5. **After deployment starts:**
   - Go to Settings → Source
   - Root Directory: `backend`
   - Save
6. **Go to Settings → Deploy**
   - Start Command: `python main.py`
   - Save
7. **Redeploy** (or wait for auto-redeploy)

### Method 2: CLI (If Dashboard Fails)

```bash
# Install CLI
iwr https://railway.app/install.ps1 | iex

# Login
railway login

# Deploy
cd backend
railway init
railway up
```

---

## 🆘 Still Having Issues?

**Please share:**
1. The exact error message from Railway logs
2. Which step fails (build or deploy)
3. Screenshot of error (if possible)

**Or try Render instead** - it's often more reliable! 🚀

