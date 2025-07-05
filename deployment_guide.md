# 🚀 CAG System Vercel Deployment Guide

## Prerequisites

1. **Vercel CLI installed:**
   ```bash
   npm install -g vercel
   ```

2. **Required Environment Variables:**
   - `GOOGLE_API_KEY` - Your Google Gemini API key
   - `REDIS_URL` - Redis connection string (use Upstash Redis for free tier)

## Step 1: Deploy Backend API

### 1.1 Login to Vercel
```bash
vercel login
```

### 1.2 Deploy Backend
```bash
# From the root directory (where vercel.json is)
vercel --prod
```

### 1.3 Set Environment Variables
```bash
# Set your Google API key
vercel env add GOOGLE_API_KEY

# Set Redis URL (get from Upstash or other Redis provider)
vercel env add REDIS_URL
```

### 1.4 Redeploy with Environment Variables
```bash
vercel --prod
```

**Note your backend URL:** `https://your-project-name.vercel.app`

## Step 2: Set Up Redis (Upstash - Free Tier)

1. Go to [Upstash](https://upstash.com/)
2. Create a free account
3. Create a new Redis database
4. Copy the Redis URL (format: `redis://...`)
5. Add it to Vercel environment variables

## Step 3: Deploy Frontend

### 3.1 Update Frontend Configuration
```bash
cd frontend
```

### 3.2 Update Environment Variables
Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-backend-url.vercel.app
```

### 3.3 Deploy Frontend
```bash
# From frontend directory
vercel --prod
```

## Step 4: Update Frontend API Routes

The frontend `vercel.json` needs to point to your actual backend URL:

```json
{
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-actual-backend-url.vercel.app/$1"
    }
  ]
}
```

## Step 5: Test Deployment

1. Visit your frontend URL
2. Test the CAG functionality
3. Check that caching works
4. Verify chat history

## Troubleshooting

### Common Issues:

1. **Redis Connection Error:**
   - Ensure REDIS_URL is correctly set
   - Use Upstash Redis for serverless compatibility

2. **CORS Issues:**
   - Backend already configured for Vercel domains
   - Check `app/main.py` CORS settings

3. **API Timeout:**
   - Vercel has 10s timeout for Hobby plan
   - Consider upgrading for longer requests

4. **Environment Variables:**
   - Use `vercel env ls` to check variables
   - Redeploy after adding new variables

## Alternative: Single Repository Deployment

If you prefer to deploy both from the same repo:

1. Move frontend to root level
2. Update vercel.json to handle both
3. Use Vercel's monorepo features

## Production Considerations

1. **Redis Provider:** Use Upstash Redis (serverless-friendly)
2. **Monitoring:** Add error tracking (Sentry)
3. **Rate Limiting:** Already implemented in backend
4. **Caching:** Redis TTL configured (1-2 hours)
5. **Security:** CORS and input validation in place

## Cost Estimation

- **Vercel:** Free tier (Hobby plan)
- **Upstash Redis:** Free tier (10K commands/day)
- **Google Gemini API:** Pay per use

Total: **$0-5/month** for moderate usage