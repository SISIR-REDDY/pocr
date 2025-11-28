# Vercel Deployment Guide

This guide will help you deploy your Optical Recognition application to Vercel.

## ⚠️ Important Considerations

### Model Size Limitations
Your application uses large ML models (PaddleOCR and TrOCR) which may exceed Vercel's serverless function limits:
- **Vercel Serverless Function Size Limit**: 50MB (uncompressed)
- **Your Models**: PaddleOCR and TrOCR models can be several hundred MB

### Recommended Solutions

1. **Option 1: Deploy Backend Separately (Recommended)**
   - Deploy backend to a service that supports large files (Railway, Render, Fly.io, or AWS/GCP)
   - Deploy frontend to Vercel
   - Update frontend environment variables to point to backend URL

2. **Option 2: Use Vercel with External Model Storage**
   - Store models in cloud storage (AWS S3, Google Cloud Storage)
   - Download models on first request (with caching)
   - This may cause cold start delays

3. **Option 3: Hybrid Approach**
   - Deploy frontend to Vercel
   - Keep backend on a VPS or cloud VM
   - Use environment variables to connect them

## Deployment Steps

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- Git repository (GitHub, GitLab, or Bitbucket)
- Your code pushed to the repository

---

## Option A: Deploy Frontend Only (Recommended for Large Models)

### Step 1: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New Project"

2. **Import Your Repository**
   - Connect your Git provider (GitHub/GitLab/Bitbucket)
   - Select your repository
   - Choose the root directory

3. **Configure Project Settings**
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build` (should auto-detect)
   - **Output Directory**: `dist` (should auto-detect)
   - **Install Command**: `npm install`

4. **Environment Variables**
   - Click "Environment Variables"
   - Add: `VITE_API_URL` = `https://your-backend-url.com`
     - Replace with your actual backend URL

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your frontend will be live at `https://your-project.vercel.app`

### Step 2: Deploy Backend Separately

Since your backend has large models, deploy it to a service that supports them:

#### Option 2a: Railway (Recommended)
1. Go to https://railway.app
2. Create new project from GitHub repo
3. Select `backend` directory
4. Railway will auto-detect Python
5. Add environment variables if needed
6. Deploy

#### Option 2b: Render
1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Deploy

#### Option 2c: Fly.io
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. In `backend` directory: `fly launch`
3. Follow prompts
4. Deploy: `fly deploy`

### Step 3: Update Frontend Environment Variable

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update `VITE_API_URL` to your backend URL
3. Redeploy frontend (or it will auto-redeploy)

---

## Option B: Deploy Both to Vercel (May Hit Size Limits)

### Step 1: Deploy Backend First

1. **Create Backend Project in Vercel**
   - Go to Vercel Dashboard
   - Click "Add New Project"
   - Import repository
   - **Root Directory**: `backend`
   - **Framework Preset**: Other
   - **Build Command**: Leave empty (or `pip install -r requirements.txt`)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

2. **Configure vercel.json**
   - The `backend/vercel.json` file is already configured
   - Ensure `api/index.py` exists (already created)

3. **Environment Variables** (if needed)
   - Add any required environment variables
   - Example: `PORT=8000`

4. **Deploy**
   - Click "Deploy"
   - Note the deployment URL (e.g., `https://your-backend.vercel.app`)

### Step 2: Deploy Frontend

1. **Create Frontend Project in Vercel**
   - Go to Vercel Dashboard
   - Click "Add New Project"
   - Import same repository
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

2. **Update Environment Variables**
   - Add: `VITE_API_URL` = `https://your-backend.vercel.app`
   - Update `frontend/vercel.json` with your backend URL:
     ```json
     {
       "rewrites": [
         {
           "source": "/api/(.*)",
           "destination": "https://your-backend.vercel.app/api/$1"
         }
       ]
     }
     ```

3. **Deploy**
   - Click "Deploy"
   - Your frontend will be live

### Step 3: Update CORS in Backend

If deploying separately, update CORS in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Manual Steps Summary

### For Frontend Deployment:
1. ✅ Code is already updated to use environment variables
2. ✅ `vercel.json` is configured
3. ⚠️ **You need to**: Update `VITE_API_URL` environment variable in Vercel dashboard
4. ⚠️ **You need to**: Update `frontend/vercel.json` with your backend URL (if using rewrites)

### For Backend Deployment:
1. ✅ `api/index.py` is created for Vercel serverless functions
2. ✅ `vercel.json` is configured
3. ⚠️ **You need to**: Ensure models are accessible (may need to download on first request)
4. ⚠️ **You need to**: Update CORS settings with frontend URL
5. ⚠️ **You need to**: Consider model size limitations

---

## Troubleshooting

### Backend Deployment Issues

**Problem**: "Function size exceeds limit"
- **Solution**: Deploy backend to Railway/Render/Fly.io instead

**Problem**: "Models not found"
- **Solution**: Models need to be downloaded on first request or stored externally

**Problem**: "Cold start timeout"
- **Solution**: Increase `maxDuration` in `vercel.json` (already set to 60s)

### Frontend Deployment Issues

**Problem**: "Cannot connect to backend"
- **Solution**: Check `VITE_API_URL` environment variable is set correctly

**Problem**: "CORS errors"
- **Solution**: Update CORS settings in backend to include frontend URL

**Problem**: "API calls fail"
- **Solution**: Ensure backend is deployed and accessible, check network tab in browser

---

## Post-Deployment Checklist

- [ ] Backend is accessible at its URL
- [ ] Frontend environment variable `VITE_API_URL` is set
- [ ] CORS is configured correctly
- [ ] Test file upload works
- [ ] Test extraction works
- [ ] Test verification works
- [ ] Check Vercel function logs for errors

---

## Alternative: Monorepo Deployment

If you want to deploy both from one Vercel project:

1. Create a root `vercel.json`:
```json
{
  "builds": [
    {
      "src": "backend/api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ]
}
```

2. Update build commands in Vercel dashboard to build both

---

## Support

If you encounter issues:
1. Check Vercel function logs in dashboard
2. Check browser console for frontend errors
3. Verify environment variables are set
4. Ensure backend is accessible from frontend domain

