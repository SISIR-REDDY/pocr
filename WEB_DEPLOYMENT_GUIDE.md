# Web-Based Deployment Guide (No CLI Required)

This guide walks you through deploying using the web interfaces - no command line needed!

## ✅ Prerequisites

- [x] Code is already pushed to GitHub (✅ Done!)
- [ ] Vercel account (free) - Sign up at https://vercel.com
- [ ] Railway account (free) - Sign up at https://railway.app (for backend)

---

## Step 1: Deploy Frontend to Vercel (5 minutes)

### 1.1 Create Vercel Account
1. Go to https://vercel.com
2. Click "Sign Up" (use GitHub to sign in - easiest)
3. Authorize Vercel to access your GitHub

### 1.2 Import Project
1. In Vercel Dashboard, click **"Add New Project"**
2. You'll see your GitHub repositories
3. Find and select **"pocr"** repository
4. Click **"Import"**

### 1.3 Configure Project
1. **Project Name**: Keep default or change (e.g., "optical-recognition-frontend")
2. **Root Directory**: Click "Edit" and set to: `frontend`
3. **Framework Preset**: Should auto-detect "Vite" ✅
4. **Build Command**: Should show `npm run build` ✅
5. **Output Directory**: Should show `dist` ✅
6. **Install Command**: Should show `npm install` ✅

### 1.4 Add Environment Variable
1. Scroll down to **"Environment Variables"** section
2. Click **"Add"** or **"Add Another"**
3. **Key**: `VITE_API_URL`
4. **Value**: Leave empty for now (we'll update after backend deployment)
   - Or set to: `https://placeholder.com` (temporary)
5. Make sure it's checked for **Production**, **Preview**, and **Development**

### 1.5 Deploy
1. Click **"Deploy"** button at the bottom
2. Wait 2-3 minutes for deployment
3. Once done, you'll see: **"Congratulations! Your project has been deployed"**
4. **Copy your frontend URL** (e.g., `https://your-project.vercel.app`)
   - Click the link to open it
   - Save this URL - you'll need it!

---

## Step 2: Deploy Backend to Railway (10 minutes)

### 2.1 Create Railway Account
1. Go to https://railway.app
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub

### 2.2 Create New Project
1. In Railway Dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select **"pocr"** repository
4. Railway will ask: **"Configure a service"**
   - Click **"Add Service"** → **"GitHub Repo"**
   - Select **"pocr"** again

### 2.3 Configure Backend Service
1. Railway will auto-detect it's a Python project ✅
2. **Root Directory**: Click "Settings" → Set to: `backend`
3. **Start Command**: Should auto-detect, but verify it's: `python main.py`
4. Railway will automatically:
   - Install dependencies (`pip install -r requirements.txt`)
   - Start the server

### 2.4 Get Backend URL
1. Wait for deployment to complete (5-10 minutes first time - models download)
2. Go to **"Settings"** tab
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"** (if not auto-generated)
5. **Copy your backend URL** (e.g., `https://your-app.railway.app`)
   - Save this URL!

### 2.5 (Optional) Set Environment Variables
- Railway usually auto-detects everything
- If needed, go to **"Variables"** tab and add:
  - `PORT=8000` (usually auto-set)
  - `USE_GPU=false` (optional)

---

## Step 3: Connect Frontend to Backend (2 minutes)

### 3.1 Update Frontend Environment Variable
1. Go back to **Vercel Dashboard**
2. Select your frontend project
3. Go to **"Settings"** → **"Environment Variables"**
4. Find `VITE_API_URL`
5. Click **"Edit"** or **"..."** → **"Edit"**
6. Update **Value** to your Railway backend URL:
   - Example: `https://your-app.railway.app`
7. Make sure it's enabled for **Production**, **Preview**, **Development**
8. Click **"Save"**

### 3.2 Redeploy Frontend
1. Go to **"Deployments"** tab in Vercel
2. Click **"..."** on the latest deployment
3. Click **"Redeploy"**
4. Or push a new commit to trigger auto-deploy

---

## Step 4: Update CORS in Backend (2 minutes)

### 4.1 Update backend/main.py
1. Open `backend/main.py` in your editor
2. Find line 88 (around the CORS middleware)
3. Change from:
   ```python
   allow_origins=["*"],  # In production, specify frontend URL
   ```
4. To:
   ```python
   allow_origins=[
       "https://your-frontend.vercel.app",  # Replace with your actual frontend URL
       "http://localhost:3000"  # For local development
   ],
   ```

### 4.2 Commit and Push
```bash
git add backend/main.py
git commit -m "Update CORS with frontend URL"
git push origin main
```

Railway will automatically redeploy! ✅

---

## Step 5: Test Your Deployment (5 minutes)

### 5.1 Test Frontend
1. Visit your frontend URL: `https://your-project.vercel.app`
2. You should see the upload interface

### 5.2 Test Backend
1. Visit: `https://your-backend.railway.app/health`
2. You should see a JSON response with model status

### 5.3 Test Full Flow
1. Upload a document/image on the frontend
2. Wait for extraction
3. Verify the extracted fields appear
4. Submit for verification
5. Check results

### 5.4 Check for Errors
- **Browser Console** (F12): Check for any frontend errors
- **Vercel Logs**: Dashboard → Your Project → "Logs" tab
- **Railway Logs**: Dashboard → Your Service → "Logs" tab

---

## 🎉 You're Done!

Your application is now live! 

### Your URLs:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-app.railway.app`

### Quick Links:
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Dashboard**: https://railway.app/dashboard

---

## 🔧 Troubleshooting

### Frontend shows "Cannot connect to backend"
- ✅ Check `VITE_API_URL` is set correctly in Vercel
- ✅ Check backend is accessible (visit backend URL directly)
- ✅ Check CORS is updated in backend/main.py
- ✅ Redeploy frontend after updating environment variable

### Backend deployment fails
- ✅ Check Railway logs for errors
- ✅ Verify `requirements.txt` is correct
- ✅ Check if models are downloading (first deployment takes time)

### Models not loading
- ✅ First request may be slow (cold start)
- ✅ Check Railway logs for model download progress
- ✅ Models download automatically on first use

### CORS errors in browser
- ✅ Update `backend/main.py` with correct frontend URL
- ✅ Commit and push changes
- ✅ Wait for Railway to redeploy

---

## 📝 Notes

- **First deployment**: Backend may take 10-15 minutes (downloading models)
- **Cold starts**: First request after inactivity may be slow
- **Free tier limits**: Both Vercel and Railway have generous free tiers
- **Auto-deploy**: Both platforms auto-deploy on git push

---

## 🆘 Need Help?

1. Check logs in both Vercel and Railway dashboards
2. Verify environment variables are set correctly
3. Test backend health endpoint directly
4. Check browser console for frontend errors
5. Review `DEPLOYMENT_QUICK_START.md` for more details
