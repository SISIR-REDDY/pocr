# Railway Root Directory Fix - Step by Step

## 🔴 The Problem

Railway is analyzing the **root directory** (which has both `backend/` and `frontend/`) instead of just `backend/`.

**Error shows:**
```
./  ← Railway is looking here (wrong!)
├── backend/  ← Should look here instead
├── frontend/
```

---

## ✅ Solution: Set Root Directory in Railway

### Method 1: Railway Dashboard (Recommended)

#### Step 1: Open Your Service
1. Go to https://railway.app/dashboard
2. Click on your **service/project** (the one that's failing)

#### Step 2: Go to Settings
1. Click the **"Settings"** tab (top menu)
2. Scroll down to find **"Source"** section

#### Step 3: Set Root Directory
1. Look for **"Root Directory"** field
2. **Delete any existing value** (if any)
3. Type: `backend` (exactly, no quotes, no slash)
4. Click **"Save"** or **"Update"** button

#### Step 4: Redeploy
1. Go to **"Deployments"** tab
2. Click **"Redeploy"** button (or the three dots → Redeploy)
3. OR push a new commit to trigger redeploy

**Railway will now look in `backend/` directory!** ✅

---

### Method 2: Delete and Recreate (If Method 1 Doesn't Work)

Sometimes it's easier to start fresh:

#### Step 1: Delete Current Service
1. Railway Dashboard → Your Service
2. Settings → Danger Zone → Delete Service
3. Confirm deletion

#### Step 2: Create New Service
1. Click **"New Project"** (or **"New"** → **"Empty Project"**)
2. Click **"Deploy from GitHub repo"**
3. Select your `pocr` repository
4. **IMPORTANT:** Before clicking "Deploy Now":
   - Click **"Settings"** (gear icon)
   - Find **"Root Directory"**
   - Set to: `backend`
   - Click **"Save"**
5. Now click **"Deploy Now"**

---

### Method 3: Use Railway CLI (Most Reliable)

If dashboard keeps failing, use CLI:

#### Step 1: Install Railway CLI
```powershell
# Windows PowerShell (run as Administrator)
iwr https://railway.app/install.ps1 | iex
```

#### Step 2: Login
```bash
railway login
```
(Opens browser for authentication)

#### Step 3: Navigate to Backend
```bash
cd backend
```

#### Step 4: Initialize
```bash
railway init
```
Follow prompts:
- Create new project? **Yes**
- Project name: `optical-recognition-backend` (or any name)

#### Step 5: Deploy
```bash
railway up
```

This uploads directly from `backend/` directory - no root directory issue! ✅

---

## 🎯 Visual Guide: Where to Set Root Directory

```
Railway Dashboard
│
├─ Your Project
│   └─ Your Service
│       │
│       ├─ [Deployments Tab] ← Check logs here
│       │
│       └─ [Settings Tab] ← GO HERE!
│           │
│           ├─ General
│           ├─ Source ← CLICK THIS!
│           │   │
│           │   └─ Root Directory: [backend] ← SET THIS!
│           │
│           ├─ Deploy
│           │   └─ Start Command: python main.py ← Also set this!
│           │
│           └─ Variables
```

---

## ✅ Verification Checklist

After setting root directory, check:

- [ ] Root Directory is set to `backend` (not `/backend` or `./backend`)
- [ ] Start Command is set to `python main.py`
- [ ] Redeployed (or new deployment triggered)
- [ ] Build logs show Railway looking in `backend/` directory
- [ ] Build logs show Python detected
- [ ] Build logs show `requirements.txt` found

---

## 🔍 How to Verify It's Working

### Check Build Logs:
1. Railway Dashboard → Your Service
2. **Deployments** tab
3. Click on latest deployment
4. Check **Build Logs**

**You should see:**
```
✓ Detected Python
✓ Found requirements.txt
✓ Installing dependencies...
```

**NOT:**
```
✖ Railpack could not determine how to build
```

---

## 🆘 Still Not Working?

### Try Render Instead (Often More Reliable)

Render is often more reliable for Python deployments:

#### Step 1: Sign Up
1. Go to https://render.com
2. Sign up with GitHub (free)

#### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repository
3. Select `pocr` repository

#### Step 3: Configure
- **Name:** `optical-recognition-backend`
- **Root Directory:** `backend` ← SET THIS!
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

#### Step 4: Deploy
1. Click **"Create Web Service"**
2. Wait 15-20 minutes (first deployment)
3. Copy your URL

**Render is often more reliable than Railway!** ✅

---

## 📋 What I've Added to Help

I've created these files to help Railway detect your app:

1. ✅ `backend/nixpacks.toml` - Railway build config
2. ✅ `backend/Procfile` - Start command
3. ✅ `backend/runtime.txt` - Python version
4. ✅ `backend/railway.toml` - Railway config
5. ✅ `railway.json` - Root config

**But the main fix is still: Set Root Directory to `backend` in Railway Settings!**

---

## 🎯 Quick Summary

**The Fix:**
1. Railway Dashboard → Your Service → Settings
2. Source section → Root Directory: `backend`
3. Save and redeploy

**OR use Railway CLI:**
```bash
cd backend
railway init
railway up
```

**OR use Render instead** (often more reliable)

---

## 💡 Pro Tip

If Railway keeps having issues, **Render is often more reliable** for Python apps. Consider switching to Render for a smoother deployment experience!

