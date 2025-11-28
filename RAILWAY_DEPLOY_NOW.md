# 🚀 Railway Deployment - Step by Step Guide

Railway CLI is installed! Now let's deploy your backend.

## ✅ Option 1: Railway CLI (Fastest - 2 minutes)

### Step 1: Login to Railway
Open PowerShell and run:
```powershell
cd backend
railway login
```
This will open your browser for authentication. Click "Authorize" in the browser.

### Step 2: Initialize Project
```powershell
railway init
```
Follow prompts:
- Create new project? **Yes**
- Project name: `optical-recognition-backend` (or any name)

### Step 3: Deploy
```powershell
railway up
```
This uploads your code and deploys!

### Step 4: Get Your URL
```powershell
railway domain
```
Or check Railway dashboard for your URL.

**Done!** Your backend is live! 🎉

---

## ✅ Option 2: Railway Dashboard (If CLI doesn't work)

### Step 1: Go to Railway Dashboard
1. Visit: https://railway.app/dashboard
2. Sign up/Login with GitHub

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. If repo not listed:
   - Click **"Configure GitHub App"**
   - Authorize Railway
   - Select **"All repositories"** or your specific repo
4. Select your **"pocr"** repository

### Step 3: Configure Service (IMPORTANT!)
**Before deploying**, go to Settings:

1. **Settings** → **Source**
   - **Root Directory**: `backend` ← **SET THIS!**
   - Save

2. **Settings** → **Deploy**
   - **Start Command**: `python main.py`
   - Save

### Step 4: Deploy
1. Railway will auto-detect Python
2. Wait 15-20 minutes (first deployment - installing dependencies)
3. Check **Deployments** tab for progress

### Step 5: Get Your URL
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy your backend URL (e.g., `https://your-app.railway.app`)

---

## 🔧 Quick CLI Commands Reference

```powershell
# Navigate to backend
cd backend

# Login (opens browser)
railway login

# Create new project
railway init

# Deploy
railway up

# Get URL
railway domain

# Check status
railway status

# View logs
railway logs
```

---

## ⚠️ Important Notes

### Root Directory Issue
If you see "Railpack could not determine how to build":
- **Fix**: Set Root Directory to `backend` in Railway Settings → Source
- Or use CLI (automatically uses `backend/` directory)

### First Deployment
- Takes **15-20 minutes** (installing dependencies)
- Models download on first API request (another 10-15 min)
- Be patient! This is normal.

### Port Configuration
Your code already uses `PORT` environment variable ✅
Railway automatically sets this - no changes needed!

---

## 📋 After Deployment

Once you have your Railway URL:

1. **Update Frontend Environment Variable:**
   - Go to Vercel dashboard
   - Settings → Environment Variables
   - Update `VITE_API_URL` with your Railway URL

2. **Update CORS:**
   - Edit `backend/main.py` (line 88)
   - Change `allow_origins=["*"]` to include your frontend URL
   - Commit and push

3. **Test:**
   - Visit: `https://your-backend.railway.app/health`
   - Should return JSON with model status

---

## 🆘 Troubleshooting

### "Railpack could not determine how to build"
**Fix:** Set Root Directory to `backend` in Railway Settings

### "Module not found"
**Fix:** Check `requirements.txt` exists in `backend/` directory ✅

### "Port already in use"
**Fix:** Already handled in your code (uses PORT env var) ✅

### Deployment timeout
**Fix:** First deployment takes 15-20 min. Wait patiently.

---

## 🎯 Quick Start (CLI)

Run these commands in PowerShell:

```powershell
cd backend
railway login          # Opens browser - click Authorize
railway init           # Create project
railway up             # Deploy!
railway domain         # Get your URL
```

**That's it!** Your backend will be live in ~20 minutes! 🚀

---

## 📞 Need Help?

If you encounter issues:
1. Check Railway dashboard → Deployments → Build Logs
2. Share the error message
3. Or try Render instead (often more reliable)

---

## ✅ Summary

**CLI Method (Recommended):**
```powershell
cd backend
railway login
railway init
railway up
railway domain  # Get your URL
```

**Dashboard Method:**
1. Railway Dashboard → New Project → GitHub
2. Settings → Root Directory: `backend`
3. Settings → Start Command: `python main.py`
4. Deploy

**Your backend will be live!** 🎉

