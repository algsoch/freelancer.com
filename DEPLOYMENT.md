# Deployment Guide: Render + Vercel

## Overview
This guide will help you deploy your AI Bid Generator with:
- **Backend (FastAPI)** → Render
- **Frontend (React + Vite)** → Vercel

## Backend Deployment (Render)

### 1. Prepare Your Backend
1. Ensure your `backend/main.py` has CORS configured for all origins (already updated)
2. Create a `requirements.txt` in the backend folder if not present

### 2. Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ai-bid-generator-api` (or your choice)
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GEMINI_API_KEY`: Your Gemini API key
   - `OPENAI_API_KEY`: Your OpenAI API key (if using)
   - Any other config from your `.env` file
6. Click **Create Web Service**
7. Wait for deployment (5-10 minutes)
8. **Copy your Render URL**: `https://your-app-name.onrender.com`

## Frontend Deployment (Vercel)

### 1. Create Environment Variable
1. In the `frontend` folder, create a `.env` file:
   ```env
   VITE_API_URL=https://your-app-name.onrender.com
   ```
   Replace with your actual Render URL (without trailing slash)

### 2. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-app-name.onrender.com` (your Render URL)
6. Click **Deploy**
7. Wait for deployment (2-3 minutes)
8. **Your app is live!** 🎉

## Testing Your Deployment

1. Open your Vercel URL
2. Try generating a bid
3. Check that the frontend connects to the backend successfully
4. Monitor Render logs for any errors: Dashboard → Your Service → Logs

## Troubleshooting

### CORS Issues
- Already fixed! Backend now accepts all origins with `allow_origins=["*"]`

### Connection Refused
- Make sure your `VITE_API_URL` in Vercel environment variables matches your Render URL exactly
- Verify the backend is running on Render (check logs)

### API Key Errors
- Verify environment variables are set correctly in Render dashboard
- Make sure there are no extra spaces in API keys

### 502/504 Errors on Render
- Free tier Render services spin down after inactivity
- First request after inactivity may take 30-60 seconds

## Updating Your Deployment

### Backend Updates
- Push changes to your GitHub repository
- Render will automatically rebuild and redeploy

### Frontend Updates
- Push changes to your GitHub repository
- Vercel will automatically rebuild and redeploy

## Cost
- **Render**: Free tier available (750 hours/month)
- **Vercel**: Free tier includes unlimited deployments

## Next Steps
- [ ] Add custom domain (optional)
- [ ] Set up monitoring/analytics
- [ ] Configure GitHub Actions for CI/CD (optional)
- [ ] Add rate limiting for production use
