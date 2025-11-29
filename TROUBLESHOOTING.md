# 🔧 Troubleshooting Guide - Render Deployment

## Issue: App Stuck at "Generating dynamic prompt template..."

### Root Cause Analysis

Your app was getting stuck on the loading screen for the following reasons:

#### 1. **Automatic Prompt Generation on Page Load**
- The frontend (`app.js`) was calling `generatePrompt()` automatically when the page loads
- This happens in the `setDefaultTopic()` function which runs during initialization
- On **Render's free tier**, cold starts can take 30-60 seconds, causing this initial request to timeout

#### 2. **No Request Timeout Handling**
- The original fetch requests had no timeout mechanism
- If the backend was slow or unresponsive, the loading overlay would stay forever
- Users would see the infinite "Generating..." message with no way out

#### 3. **Cold Start Issues on Free Tier**
- Render free tier services "sleep" after 15 minutes of inactivity
- First request after sleep takes longer to wake up the service
- The app was trying to make an API call before the backend was fully ready

### Solutions Implemented ✅

#### Fix #1: Removed Auto-Generation on Page Load
```javascript
async setDefaultTopic() {
    document.getElementById('topicInput').value = 'Prompt Engineering';
    // Don't auto-generate on page load to avoid cold start issues
    // User can click "Generate Prompt" button when ready
}
```
**Why this helps:**
- Gives the backend time to fully start up
- User explicitly triggers the action when they're ready
- Better user experience - they see the app load instantly

#### Fix #2: Added Request Timeouts
```javascript
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 30000); // 30 second timeout

const response = await fetch('/api/generate-prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
    signal: controller.signal
});

clearTimeout(timeout);
```
**Applied to:**
- `/api/generate-prompt` - 30 seconds
- `/api/gemini/query` - 60 seconds
- `/api/youtube/search` - 60 seconds
- `/api/quotas` - 10 seconds
- `/api/health` - 5 seconds

#### Fix #3: Better Error Handling
```javascript
catch (error) {
    console.error('Error generating prompt:', error);
    if (error.name === 'AbortError') {
        this.showToast('Request timed out. Please try again.', 'error');
    } else {
        this.showToast(`Error: ${error.message}`, 'error');
    }
} finally {
    this.hideLoading(); // Always hide loading, even on error
}
```

#### Fix #4: Backend Health Check
```javascript
async checkBackendHealth() {
    try {
        const response = await fetch('/api/health', { signal: controller.signal });
        if (response.ok) {
            console.log('Backend is healthy and ready');
        }
    } catch (error) {
        this.showToast('Connecting to backend... Please wait a moment.', 'warning');
    }
}
```

## How to Deploy the Fixed Version

### Step 1: Commit and Push Changes
```bash
git add .
git commit -m "Fix: Prevent infinite loading on Render deployment"
git push origin main
```

### Step 2: Render Auto-Deploy
- Render will automatically detect the changes
- It will rebuild and redeploy your app
- Wait 2-3 minutes for deployment to complete

### Step 3: Test the Fix
1. Open your Render URL
2. The page should load **instantly** (no stuck loading)
3. Click "Generate Prompt" button to test functionality
4. If backend is waking up from sleep, you'll see a warning toast

## Understanding Render Free Tier Behavior

### Cold Starts
- **First request after 15min**: 30-60 seconds response time
- **Subsequent requests**: Near-instant (< 1 second)
- **Solution**: The app now handles this gracefully

### Keep-Alive Strategy
Your repo includes `.github/workflows/keep-alive.yml` which:
- Pings your service every 14 minutes
- Prevents it from sleeping
- Keeps response times fast

**Make sure this workflow is enabled:**
1. Go to GitHub → Actions tab
2. Enable workflows if disabled
3. The keep-alive will run automatically

## Testing Checklist

After deployment, verify:

- [ ] Page loads instantly without infinite spinner
- [ ] Default topic appears in input field ("Prompt Engineering")
- [ ] Clicking "Generate Prompt" works correctly
- [ ] All API calls have proper error messages if they fail
- [ ] Loading overlay disappears after timeout (max 30-60 seconds)
- [ ] Toast notifications show for errors and timeouts
- [ ] Quota cards load (or fail gracefully if backend is slow)
- [ ] Quick topics load and are clickable

## Common Issues After Fix

### Issue: "Request timed out" message appears
**Cause:** Backend is cold starting (waking up from sleep)
**Solution:** Click the button again after 10-20 seconds

### Issue: Backend health check fails
**Cause:** Service is still deploying or starting up
**Solution:** Wait 1-2 minutes and refresh the page

### Issue: GitHub Actions keep-alive not working
**Check:**
1. GitHub Actions is enabled in your repo settings
2. Workflow file exists: `.github/workflows/keep-alive.yml`
3. The workflow has the correct Render URL

## Monitoring Your App

### View Logs on Render:
1. Go to render.com dashboard
2. Select your service
3. Click "Logs" tab
4. Watch for:
   - `Application startup complete`
   - API request logs
   - Error messages

### Check Discord Webhook:
Your app logs all activity to Discord, including:
- Visitor logs
- API requests
- Errors and exceptions

## Performance Tips

### For Better Free Tier Experience:
1. **Keep GitHub Actions enabled** - Prevents cold starts
2. **Set up a custom domain** - Makes your URL memorable
3. **Monitor Discord logs** - Track when service goes to sleep
4. **Test during quiet hours** - See actual cold start behavior

### For Production (Paid Tier):
1. Upgrade to **Starter Plan ($7/month)** for:
   - No cold starts
   - Always-on service
   - Better performance
   - More resources

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [GitHub Actions Keep-Alive](https://github.com/marketplace/actions/keepalive-workflow)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/deployment/)

## Need Help?

If you're still experiencing issues:

1. **Check Render logs** for errors
2. **Check Discord webhook** for request logs
3. **Test locally** with `python backend/main.py`
4. **Check browser console** for frontend errors (F12 → Console)

---

**Fixed by:** Vicky Kumar (@algsoch)
**Date:** November 29, 2025
**Version:** 1.0.1
