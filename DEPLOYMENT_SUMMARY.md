# Deployment Setup Summary

## ✅ What Has Been Done Automatically

### Frontend Changes
1. ✅ Created `frontend/src/config.js` - Centralized API URL configuration
2. ✅ Updated `frontend/src/App.jsx` - Now uses environment variable for API calls
3. ✅ Updated `frontend/src/components/UploadBox.jsx` - Now uses environment variable for API calls
4. ✅ Created `frontend/vercel.json` - Vercel configuration for frontend
5. ✅ Created `frontend/.env.example` - Example environment variables (if not blocked)

### Backend Changes
1. ✅ Created `backend/api/index.py` - Vercel serverless function entry point
2. ✅ Created `backend/vercel.json` - Vercel configuration for backend
3. ✅ Backend is ready for deployment (though large models may require alternative hosting)

### Root Configuration
1. ✅ Created `vercel.json` - Root-level configuration for monorepo deployment
2. ✅ Created `.vercelignore` - Files to ignore during deployment

### Documentation
1. ✅ Created `docs/vercel-deployment.md` - Comprehensive deployment guide
2. ✅ Created `DEPLOYMENT_QUICK_START.md` - Quick reference guide

---

## ⚠️ What You Need to Do Manually

### 1. Deploy Frontend to Vercel

**Steps:**
1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import your Git repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Vite (auto-detected)
5. Add Environment Variable:
   - Name: `VITE_API_URL`
   - Value: `https://your-backend-url.com` (you'll set this after backend deployment)
6. Click "Deploy"
7. Note your frontend URL

### 2. Deploy Backend

**Recommended: Use Railway, Render, or Fly.io** (due to large model files)

#### Option A: Railway
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select `backend` directory
4. Deploy (auto-detects Python)
5. Copy the deployment URL

#### Option B: Render
1. Go to https://render.com
2. New Web Service
3. Connect GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
5. Deploy
6. Copy the URL

#### Option C: Vercel (May hit size limits)
1. Go to Vercel Dashboard
2. New Project → Import repository
3. Root Directory: `backend`
4. Deploy
5. Note: May fail if models exceed 50MB limit

### 3. Connect Frontend to Backend

1. **Update Frontend Environment Variable:**
   - Go to Vercel → Your Frontend Project → Settings → Environment Variables
   - Update `VITE_API_URL` with your backend URL
   - Redeploy

2. **Update Backend CORS (if deploying separately):**
   - Edit `backend/main.py`
   - Change line 88 from:
     ```python
     allow_origins=["*"],  # In production, specify frontend URL
     ```
   - To:
     ```python
     allow_origins=[
         "https://your-frontend.vercel.app",
         "http://localhost:3000"  # For local dev
     ],
     ```

### 4. Test Deployment

1. Visit your frontend URL
2. Try uploading a document
3. Check browser console for errors
4. Check backend logs for any issues

---

## 📝 Environment Variables Reference

### Frontend (Vercel)
- `VITE_API_URL` - Your backend API URL (e.g., `https://your-backend.railway.app`)

### Backend (Railway/Render/etc.)
- `PORT` - Server port (default: 8000, usually auto-set by platform)
- `USE_GPU` - Enable GPU (optional, default: false)

---

## 🔍 File Structure After Changes

```
opticalrecog/
├── backend/
│   ├── api/
│   │   └── index.py          ← NEW: Vercel serverless handler
│   ├── vercel.json           ← NEW: Backend Vercel config
│   └── main.py               ← Existing (CORS may need update)
├── frontend/
│   ├── src/
│   │   ├── config.js         ← NEW: API URL configuration
│   │   ├── App.jsx           ← UPDATED: Uses config.js
│   │   └── components/
│   │       └── UploadBox.jsx ← UPDATED: Uses config.js
│   └── vercel.json           ← NEW: Frontend Vercel config
├── vercel.json               ← NEW: Root monorepo config
├── .vercelignore            ← NEW: Ignore patterns
├── DEPLOYMENT_QUICK_START.md ← NEW: Quick guide
├── DEPLOYMENT_SUMMARY.md     ← NEW: This file
└── docs/
    └── vercel-deployment.md  ← NEW: Full deployment guide
```

---

## 🚨 Important Warnings

1. **Model Size**: Your PaddleOCR and TrOCR models are large (hundreds of MB). Vercel serverless functions have a 50MB limit. **Deploy backend to Railway/Render/Fly.io instead.**

2. **Cold Starts**: If using serverless, the first request will be slow as models load. Consider keeping a warm instance.

3. **CORS**: Currently set to allow all origins (`["*"]`). Update this in production for security.

4. **Environment Variables**: Must be set in Vercel dashboard. They're not automatically deployed.

---

## 📚 Next Steps

1. Read `DEPLOYMENT_QUICK_START.md` for step-by-step instructions
2. Read `docs/vercel-deployment.md` for detailed options
3. Deploy frontend to Vercel
4. Deploy backend to Railway/Render/Fly.io
5. Connect them with environment variables
6. Test and verify everything works

---

## 🆘 Need Help?

- Check Vercel function logs in dashboard
- Check browser console for frontend errors
- Verify environment variables are set correctly
- Ensure backend is accessible from frontend domain
- Review `docs/vercel-deployment.md` for troubleshooting

