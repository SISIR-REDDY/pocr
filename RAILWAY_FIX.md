# Railway Deployment Fix - Root Directory Issue

## 🔴 Error You're Seeing

```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
```

**Problem:** Railway is analyzing the **root directory** instead of the `backend/` directory.

---

## ✅ Solution: Set Root Directory in Railway Dashboard

### Step 1: Go to Railway Settings

1. Open Railway dashboard
2. Select your service/project
3. Click **"Settings"** tab
4. Scroll to **"Source"** section

### Step 2: Set Root Directory

1. Find **"Root Directory"** field
2. Enter: `backend`
3. Click **"Save"**

### Step 3: Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** or push a new commit
3. Railway will now look in `backend/` directory ✅

---

## 🎯 Alternative: Use Railway CLI

If dashboard doesn't work, use CLI:

```bash
# Install Railway CLI
iwr https://railway.app/install.ps1 | iex

# Login
railway login

# Link to project
cd backend
railway link

# Set root directory (if needed)
railway variables set RAILWAY_ROOT_DIRECTORY=backend

# Deploy
railway up
```

---

## 📋 What I've Added

I've created configuration files to help Railway detect your app:

1. ✅ `backend/Procfile` - Tells Railway how to start
2. ✅ `backend/nixpacks.toml` - Railway build configuration
3. ✅ `railway.json` - Railway deployment config

---

## 🚀 Quick Fix Steps

### Option 1: Railway Dashboard (Easiest)

1. **Railway Dashboard** → Your Service → **Settings**
2. **Source** section → **Root Directory**: `backend`
3. **Save**
4. **Redeploy** (or push new commit)

### Option 2: Delete and Recreate Service

1. Delete current service in Railway
2. **New Project** → **Deploy from GitHub**
3. Select repository
4. **Before deploying**, go to Settings:
   - **Root Directory**: `backend`
   - **Start Command**: `python main.py`
5. **Deploy**

---

## ✅ Verification

After setting root directory, Railway should:
- ✅ Find `backend/requirements.txt`
- ✅ Find `backend/main.py`
- ✅ Auto-detect Python
- ✅ Install dependencies
- ✅ Start your app

---

## 🆘 Still Not Working?

### Try Render Instead (Often More Reliable)

1. Go to https://render.com
2. **New Web Service** → Connect GitHub
3. **Root Directory**: `backend`
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python main.py`
6. **Deploy**

Render is often more reliable for Python apps!

---

## 📝 Summary

**The fix:** Set **Root Directory** to `backend` in Railway Settings.

**Steps:**
1. Railway Dashboard → Settings → Source
2. Root Directory: `backend`
3. Save and redeploy

That's it! 🎉

