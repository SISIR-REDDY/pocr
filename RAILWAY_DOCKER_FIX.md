# Railway Docker Build Failure - Fix Guide

## 🔴 Problem Identified

Your Railway deployment is failing at the **"importing to docker"** step. This is likely because:

1. **Models are being copied** (5.7GB) - causing build timeout/failure
2. **Docker build context too large**
3. **Build timeout** during Docker import

## ✅ Solution: Exclude Models from Docker Build

The models should **NOT** be in the Docker build - they download on-demand!

### Fix 1: Update .dockerignore

I've already created `.dockerignore` but let's verify it's correct:

```
models/
*.bin
*.safetensors
*.onnx
*.pt
*.pth
```

### Fix 2: Update Dockerfile (If Using Docker)

If Railway is using Docker, we need to ensure models aren't copied:

```dockerfile
# Don't copy models - they download on-demand
COPY . .
# But exclude models directory
RUN rm -rf models/*.bin models/*.safetensors models/*.pt models/*.pth 2>/dev/null || true
```

### Fix 3: Use Nixpacks Instead of Docker (Recommended)

Railway should use **Nixpacks** (auto-detects Python), not Docker.

**Check Railway Settings:**
1. Go to Railway Dashboard → Your Service → Settings
2. **Build** section
3. **Builder**: Should be `NIXPACKS` (not Docker)
4. If it's Docker, change to Nixpacks

---

## 🚀 Quick Fix Steps

### Step 1: Remove Dockerfile (If Present)

Railway should auto-detect Python and use Nixpacks. If you have a Dockerfile, it might be forcing Docker build.

**Option A: Delete Dockerfile**
```bash
# Don't delete, just rename it
mv backend/Dockerfile backend/Dockerfile.backup
```

**Option B: Or ensure .dockerignore excludes models**

### Step 2: Verify .dockerignore

Make sure `backend/.dockerignore` exists and excludes models:

```
models/
*.bin
*.safetensors
venv/
__pycache__/
*.pyc
```

### Step 3: Set Builder to Nixpacks

1. Railway Dashboard → Your Service → Settings
2. **Build** section
3. **Builder**: Select `NIXPACKS` (not Docker)
4. Save

### Step 4: Redeploy

1. Go to Deployments tab
2. Click **"Redeploy"**
3. Or push a new commit

---

## 🎯 Alternative: Use Railway CLI (Bypasses Docker)

If dashboard keeps failing, use CLI:

```powershell
cd backend
railway login
railway init
railway up
```

CLI uses Nixpacks automatically (no Docker issues).

---

## 📋 What Should Happen

**Correct Build Process:**
1. ✅ Detect Python
2. ✅ Install system dependencies (poppler-utils, etc.)
3. ✅ Install Python packages from requirements.txt
4. ✅ Copy code (excluding models)
5. ✅ Start with `python main.py`
6. ✅ Models download on first request (not during build)

**Your Current Issue:**
- Build is trying to copy models (5.7GB) into Docker
- This causes timeout/failure

---

## ✅ Verification

After fix, build logs should show:
- ✅ No model files being copied
- ✅ Build completes in < 5 minutes
- ✅ Deployment succeeds
- ✅ Models download on first API request (not during build)

---

## 🆘 Still Failing?

If still failing after fixes:

1. **Check Build Logs** for specific error
2. **Try Railway CLI** instead of dashboard
3. **Or use Render** (often more reliable for Python)

---

## 📝 Summary

**The Fix:**
1. Ensure `.dockerignore` excludes models ✅
2. Set Builder to `NIXPACKS` in Railway Settings
3. Remove/rename Dockerfile (if forcing Docker build)
4. Redeploy

**Models should NOT be in build - they download on-demand!** ✅

