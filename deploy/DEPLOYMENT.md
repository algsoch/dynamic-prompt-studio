# 🚀 Deployment Guide

This guide covers multiple deployment options for your Dynamic Prompt Template Studio.

## 📋 Pre-Deployment Checklist

- [ ] `.env` file configured with your API keys
- [ ] Discord webhook URL set up
- [ ] Code pushed to GitHub repository
- [ ] Docker Hub account created (for Docker deployments)

## 🌐 Recommended Deployment Platforms

### 1. 🚄 Railway (Easiest & Free)

**Perfect for: Beginners, quick deployment, free hosting**

```bash
# Run the automated script
chmod +x deploy/railway.sh
./deploy/railway.sh
```

**Manual steps:**
1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set environment variables:
   ```bash
   railway variables set GEMINI_API_KEY="your_key"
   railway variables set DISCORD_WEBHOOK_URL="your_webhook"
   ```
5. Deploy: `railway up`

**Cost:** Free tier with generous limits

---

### 2. 🎨 Render (Great for Production)

**Perfect for: Production apps, automatic deploys, custom domains**

```bash
# View instructions
./deploy/render.sh
```

**Steps:**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service" → "Docker"
4. Set environment variables in dashboard
5. Deploy automatically

**Cost:** Free tier available, $7/month for always-on

---

### 3. 🐳 Docker Hub + Cloud Platforms

**Perfect for: Scalable deployments, enterprise use**

```bash
# Build and push Docker image
chmod +x deploy/docker.sh
./deploy/docker.sh
```

**Then deploy to:**
- **DigitalOcean App Platform**
- **AWS App Runner / ECS**
- **Google Cloud Run**
- **Azure Container Instances**

---

### 4. 🌊 DigitalOcean App Platform

**Perfect for: Managed hosting, predictable pricing**

1. Login to [DigitalOcean](https://cloud.digitalocean.com)
2. Create new App
3. Connect GitHub repository
4. Choose "Docker" as build method
5. Set environment variables
6. Deploy

**Cost:** $5-$25/month

---

### 5. ☁️ Heroku (Traditional)

**Perfect for: Simple deployments, add-ons ecosystem**

```bash
# Install Heroku CLI
# Create app
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key
heroku config:set DISCORD_WEBHOOK_URL=your_webhook

# Deploy
git push heroku main
```

**Cost:** $7/month minimum

---

## ⚙️ Environment Variables

All platforms need these environment variables:

### Required:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
PYTHONPATH=/app
PORT=8000
HOST=0.0.0.0
```

### Optional (for full functionality):
```env
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## 🔧 Platform-Specific Configuration

### Railway
- Automatically detects Python
- Uses Dockerfile if present
- Free tier: 500 hours/month

### Render
- Requires Dockerfile
- Automatic deploys from GitHub
- Free tier sleeps after 15 minutes

### DigitalOcean
- App Platform supports Docker
- Predictable pricing
- Built-in monitoring

### Heroku
- Requires `Procfile` (optional with Docker)
- Extensive add-on ecosystem
- Automatic SSL

## 🔒 Security Considerations

### Production Settings:
1. Set `DEBUG=false` in environment
2. Use strong secret keys
3. Configure CORS properly
4. Enable HTTPS
5. Rotate API keys regularly

### Environment Variables Security:
- Never commit `.env` to Git
- Use platform secret management
- Rotate keys periodically
- Monitor API usage

## 📊 Monitoring & Logging

Your app includes built-in monitoring:

- **Health Check**: `GET /api/health`
- **Discord Logging**: All requests logged to Discord
- **API Quota Tracking**: Real-time usage monitoring

### Additional Monitoring:
- **Render**: Built-in metrics
- **Railway**: Resource usage tracking
- **DigitalOcean**: App insights
- **Heroku**: Logs and metrics

## 🚨 Troubleshooting

### Common Issues:

1. **App won't start**
   - Check environment variables
   - Verify port configuration (usually 8000)
   - Check logs for Python errors

2. **API keys not working**
   - Verify keys are set correctly
   - Check API quotas and billing
   - Test with demo mode first

3. **Discord logging not working**
   - Verify webhook URL format
   - Check Discord server permissions
   - Test webhook manually

4. **Static files not loading**
   - Verify file paths in FastAPI
   - Check Docker COPY commands
   - Ensure files are not in .dockerignore

### Debug Commands:
```bash
# Check if app starts locally
python backend/main.py

# Test Docker build
docker build -t test-app .
docker run -p 8000:8000 test-app

# Check environment variables
printenv | grep -E "(GEMINI|DISCORD|YOUTUBE)"
```

## 🎯 Recommended Deployment Path

1. **Start with Railway** (free, easy setup)
2. **Move to Render** (production-ready, custom domain)
3. **Scale with DigitalOcean/AWS** (high traffic, enterprise)

## 📞 Support

If you encounter issues:
1. Check the logs on your deployment platform
2. Test locally first
3. Verify environment variables
4. Check API key quotas
5. Review Discord webhook configuration

---

**Happy deploying! 🚀**

Built by **Vicky Kumar (@algsoch)**