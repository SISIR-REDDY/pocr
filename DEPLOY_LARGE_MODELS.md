# 🚀 Deploying with Large Models (5.7GB) - Step by Step

Your models are **5.69 GB**, which is too large for most platforms. Here's how to deploy:

## ✅ Solution: On-Demand Model Download

Models will be downloaded from Hugging Face Hub on first request, not included in deployment.

---

## 📋 Step-by-Step Deployment

### Step 1: Prepare Repository

✅ **Already Done!** Code is updated to download models on-demand.

### Step 2: Deploy Backend to Railway (Recommended)

Railway handles large downloads well and has persistent storage.

#### 2.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Authorize Railway

#### 2.2 Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **"pocr"** repository

#### 2.3 Configure Service
1. Railway will auto-detect Python
2. Go to **Settings** → **Root Directory**: Set to `backend`
3. **Start Command**: `python main.py`
4. Railway will auto-install dependencies

#### 2.4 Set Environment Variables (Optional)
- `PORT=8000` (usually auto-set)
- `USE_GPU=false` (CPU is fine)

#### 2.5 Deploy
1. Click **"Deploy"**
2. **First deployment takes 15-20 minutes** (installing dependencies)
3. Models will download on first API request (another 10-15 min)

#### 2.6 Get Backend URL
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy your backend URL (e.g., `https://your-app.railway.app`)

---

### Step 3: Deploy Frontend to Vercel

#### 3.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

#### 3.2 Import Project
1. Click **"Add New Project"**
2. Select **"pocr"** repository
3. **Root Directory**: `frontend`
4. Framework auto-detects as **Vite** ✅

#### 3.3 Add Environment Variable
1. Scroll to **"Environment Variables"**
2. Add:
   - **Key**: `VITE_API_URL`
   - **Value**: Your Railway backend URL (from Step 2.6)
   - Check: Production, Preview, Development

#### 3.4 Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes
3. Copy your frontend URL

---

### Step 4: Update CORS

1. Edit `backend/main.py` (line 88)
2. Change:
   ```python
   allow_origins=["*"],
   ```
3. To:
   ```python
   allow_origins=[
       "https://your-frontend.vercel.app",  # Your Vercel URL
       "http://localhost:3000"
   ],
   ```
4. Commit and push:
   ```bash
   git add backend/main.py
   git commit -m "Update CORS with frontend URL"
   git push origin main
   ```
5. Railway will auto-redeploy ✅

---

### Step 5: Test Deployment

#### 5.1 Test Backend
1. Visit: `https://your-backend.railway.app/health`
2. Should return JSON with model status
3. **First request**: May take 10-15 min (downloading models)
4. **Subsequent requests**: Fast ✅

#### 5.2 Test Frontend
1. Visit your Vercel frontend URL
2. Upload a document
3. Wait for extraction (first time may be slow)
4. Verify it works!

---

## ⚠️ Important Notes

### First Request Behavior
- **First API request**: Takes 10-15 minutes
  - Models download from Hugging Face
  - ~5.7GB download
  - Be patient!
- **Subsequent requests**: Fast (models cached)

### Model Caching
- Models are cached in Railway's filesystem
- **After inactivity**: Container may restart (models re-download)
- **Railway Pro**: Keeps containers warm (no re-download)

### Cold Starts
- After 30+ min inactivity, container may sleep
- First request after sleep: Slow (model download)
- Consider Railway Pro ($20/month) for always-on

---

## 🔧 Alternative: Use Smaller Models

If downloads are too slow, consider using smaller models:

### Option 1: Use Base Models Instead of Large
- `microsoft/trocr-base-handwritten` (smaller)
- `microsoft/trocr-base-printed` (smaller)
- Update `backend/services/model_downloader.py`

### Option 2: Model Quantization
- Convert models to INT8 (4x smaller)
- Requires model conversion script
- May reduce accuracy slightly

---

## 💰 Cost Options

### Free Tier (Current Setup)
- **Railway**: Free tier (500 hours/month)
- **Vercel**: Free tier (unlimited)
- **Models**: Downloaded on-demand (free)
- **Issue**: Cold starts re-download models

### Paid Tier (Recommended for Production)
- **Railway Pro**: $20/month
  - Always-on containers
  - No cold starts
  - Models stay cached
- **Vercel**: Still free

---

## 🆘 Troubleshooting

### Models Not Downloading
- Check Railway logs for errors
- Verify internet connection in container
- Check Hugging Face Hub is accessible

### First Request Timeout
- Railway free tier: 60s timeout
- First download takes 10-15 min
- **Solution**: Use Railway Pro or pre-download models

### Out of Memory
- Models need ~6GB RAM when loading
- Railway free tier: 512MB RAM ❌
- **Solution**: Upgrade to Railway Pro (2GB RAM) or use smaller models

### Models Re-download Every Time
- Railway free tier clears filesystem on restart
- **Solution**: Use Railway Pro (persistent storage)

---

## 📊 Platform Comparison for Large Models

| Platform | Free Tier | Model Support | Best For |
|----------|-----------|---------------|----------|
| **Railway** | 500 hrs/mo | ✅ (on-demand) | Recommended |
| **Render** | Free tier | ⚠️ (512MB limit) | Not recommended |
| **Fly.io** | 3GB storage | ✅ (if fits) | Alternative |
| **DigitalOcean** | $6/mo | ✅ (full control) | Production |
| **AWS EC2** | 1yr free | ✅ (full control) | Production |

---

## ✅ Quick Checklist

- [ ] Deploy backend to Railway
- [ ] Set root directory to `backend`
- [ ] Get backend URL
- [ ] Deploy frontend to Vercel
- [ ] Set `VITE_API_URL` environment variable
- [ ] Update CORS in `backend/main.py`
- [ ] Commit and push CORS changes
- [ ] Test backend health endpoint
- [ ] Test frontend upload
- [ ] Wait patiently for first model download (10-15 min)

---

## 🎯 Summary

1. **Deploy backend to Railway** (handles large downloads)
2. **Deploy frontend to Vercel** (fast, free)
3. **Models download automatically** on first request
4. **First request is slow** (10-15 min) - be patient!
5. **Subsequent requests are fast** (models cached)

**Your deployment is ready!** Just follow the steps above. 🚀

