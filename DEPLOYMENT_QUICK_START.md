# Quick Deployment Guide to Vercel

## 🚀 Quick Start (Recommended: Separate Deployments)

### Step 1: Deploy Frontend to Vercel

1. **Push your code to GitHub/GitLab/Bitbucket**

2. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New Project"
   - Import your repository

3. **Configure Frontend Project**
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

4. **Add Environment Variable**
   - Go to Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend-url.com`
   - (You'll update this after deploying backend)

5. **Deploy**
   - Click "Deploy"
   - Note your frontend URL: `https://your-frontend.vercel.app`

### Step 2: Deploy Backend (Choose One)

#### Option A: Railway (Easiest for Large Models)
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select `backend` directory
4. Railway auto-detects Python
5. Deploy
6. Copy the URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to https://render.com
2. New Web Service → Connect GitHub
3. Settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
4. Deploy
5. Copy the URL

#### Option C: Fly.io
```bash
cd backend
fly launch
fly deploy
```

### Step 3: Connect Frontend to Backend

1. **Update Frontend Environment Variable**
   - Go to Vercel Dashboard → Your Frontend Project
   - Settings → Environment Variables
   - Update `VITE_API_URL` to your backend URL
   - Redeploy (or wait for auto-redeploy)

2. **Update Backend CORS** (if needed)
   - Edit `backend/main.py`
   - Update `allow_origins` to include your frontend URL:
   ```python
   allow_origins=[
       "https://your-frontend.vercel.app",
       "http://localhost:3000"
   ]
   ```

3. **Test**
   - Visit your frontend URL
   - Try uploading a document
   - Check browser console for errors

---

## 📋 Manual Steps Checklist

### Frontend Deployment
- [x] Code updated to use environment variables ✅
- [x] `vercel.json` configured ✅
- [ ] **YOU NEED TO**: Set `VITE_API_URL` in Vercel dashboard
- [ ] **YOU NEED TO**: Deploy frontend project

### Backend Deployment
- [x] `api/index.py` created for Vercel ✅
- [x] `vercel.json` configured ✅
- [ ] **YOU NEED TO**: Deploy backend (Railway/Render/Fly.io recommended)
- [ ] **YOU NEED TO**: Update CORS with frontend URL
- [ ] **YOU NEED TO**: Test backend health endpoint

### Post-Deployment
- [ ] Test file upload
- [ ] Test extraction
- [ ] Test verification
- [ ] Check function logs for errors

---

## ⚠️ Important Notes

1. **Model Size**: Your ML models are large. Vercel serverless functions have a 50MB limit. That's why we recommend deploying backend separately.

2. **Environment Variables**: The frontend now uses `VITE_API_URL` environment variable. Make sure to set it in Vercel dashboard.

3. **CORS**: If you deploy separately, update CORS in `backend/main.py` to allow your frontend domain.

4. **Cold Starts**: If using serverless, first request may be slow (model loading). Consider keeping a warm instance.

---

## 🔧 Troubleshooting

**Frontend can't connect to backend?**
- Check `VITE_API_URL` is set correctly
- Check backend is accessible
- Check CORS settings

**Backend deployment fails?**
- Check model files aren't too large
- Check logs for errors
- Consider Railway/Render instead of Vercel for backend

**Models not loading?**
- Models download on first use
- May take time on first request
- Check logs for download errors

---

## 📚 Full Documentation

See `docs/vercel-deployment.md` for detailed instructions and alternative deployment options.

