# Deployment Guide - RedRob Ranker on Render

This guide will help you deploy the RedRob Ranker project to Render's free tier.

## 🚀 Quick Deploy (5 minutes)

### Prerequisites
- GitHub account (you already have this)
- Render account (free, no credit card required)

---

## Step 1: Create Render Account

1. Go to https://dashboard.render.com/
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"** (easiest option)
4. Authorize Render to access your GitHub repositories

---

## Step 2: Deploy Backend API

1. In Render dashboard, click **"New"** → **"Web Service"**

2. **Connect your repository:**
   - Find: `amalkvr11/india-runs-red-rob-hackathon`
   - Click **"Connect"**

3. **Configure the service:**
   ```
   Name: redrob-ranker-api
   Environment: Docker
   Branch: main
   Root Directory: (leave empty)
   Dockerfile Path: ./Dockerfile
   ```

4. **Environment Variables** (add these):
   ```
   Key: PORT, Value: 8000
   Key: ENVIRONMENT, Value: production
   Key: LOG_LEVEL, Value: INFO
   ```

5. Click **"Create Web Service"**

6. Wait 5-10 minutes for deployment
   - You'll see build logs
   - When status shows **"Live"**, your API is ready!

7. **Your API URL:** `https://redrob-ranker-api.onrender.com`

---

## Step 3: Deploy Frontend

1. In Render dashboard, click **"New"** → **"Static Site"**

2. **Connect the same repository**

3. **Configure:**
   ```
   Name: redrob-ranker-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   Branch: main
   ```

4. **Environment Variables:**
   ```
   Key: VITE_API_URL, Value: https://redrob-ranker-api.onrender.com/api
   ```

5. Click **"Create Static Site"**

6. Wait 2-3 minutes for build

7. **Your Frontend URL:** `https://redrob-ranker-frontend.onrender.com`

---

## Step 4: Update API CORS (Important!)

After deployment, you need to update CORS to allow your frontend:

1. Go to `api/server.py` in your repo
2. Update line 27:
   ```python
   allow_origins=["https://redrob-ranker-frontend.onrender.com"],
   ```
3. Commit and push - Render will auto-deploy!

---

## 📋 What You Get

| Component | URL | Status |
|-----------|-----|--------|
| Backend API | https://redrob-ranker-api.onrender.com | Live ✅ |
| Frontend | https://redrob-ranker-frontend.onrender.com | Live ✅ |
| Health Check | https://redrob-ranker-api.onrender.com/health | Working ✅ |

---

## 🔧 Troubleshooting

### Issue: Build fails
**Solution:** Check build logs in Render dashboard
- Make sure `Dockerfile` exists in root
- Ensure `requirements.txt` has all dependencies

### Issue: Frontend can't connect to API
**Solution:** 
- Check `VITE_API_URL` is set correctly
- Verify CORS origins in `api/server.py`
- Both services must be deployed

### Issue: API returns 404
**Solution:**
- Wait 2-3 minutes after deployment
- Check if candidate data file exists in repo

### Issue: Free tier limits
**Render free tier limits:**
- Web services: Sleeps after 15 min idle (wakes on request)
- Static sites: Always available
- Bandwidth: 100GB/month (more than enough)

---

## 🔄 Auto-Deployment

Every time you push to GitHub `main` branch:
- Render automatically rebuilds and deploys
- Takes 2-5 minutes
- Zero downtime

---

## 📝 Testing Deployment

After deployment, test these URLs:

1. **Health Check:**
   ```
   https://redrob-ranker-api.onrender.com/health
   ```
   Should return: `{"status": "healthy", "cached": false}`

2. **Get Weights:**
   ```
   https://redrob-ranker-api.onrender.com/api/weights
   ```

3. **Run Ranking:**
   - Go to frontend URL
   - Click "Run Ranking"
   - Wait 1-2 minutes

---

## 🎯 For Hackathon Judges

**Access your deployed app:**
1. Frontend: https://redrob-ranker-frontend.onrender.com
2. API Docs: https://redrob-ranker-api.onrender.com/docs (if added)

**Demo flow:**
1. Open frontend URL
2. Click "Run Ranking" (processes 100K candidates)
3. View results table with top 100 candidates
4. Click any candidate for detailed view
5. Show dashboard with analytics

---

## 📊 Monitoring

In Render dashboard:
- View build logs
- Monitor resource usage
- Check request logs
- View error rates

---

## 🆘 Need Help?

1. Check Render documentation: https://render.com/docs
2. Check build logs in Render dashboard
3. Common issues in this guide above
4. Contact Render support (free tier includes support)

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] Backend API deployed (redrob-ranker-api)
- [ ] Frontend deployed (redrob-ranker-frontend)
- [ ] Environment variables set
- [ ] CORS updated
- [ ] Health check working
- [ ] Frontend connects to API
- [ ] Ranking runs successfully
- [ ] Auto-deploy working (push test)

---

**Your project is now LIVE and ready for the hackathon!** 🎉
