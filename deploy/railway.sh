#!/bin/bash

# Deploy to Railway
echo "🚀 Deploying to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Logging in to Railway..."
railway login

# Initialize project (if not already initialized)
if [ ! -f "railway.json" ]; then
    echo "🆕 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
read -p "Enter your Gemini API Key (or press Enter to skip): " GEMINI_KEY
read -p "Enter your YouTube API Key (or press Enter to skip): " YOUTUBE_KEY
read -p "Enter your Discord Webhook URL: " DISCORD_URL

if [ ! -z "$GEMINI_KEY" ]; then
    railway variables set GEMINI_API_KEY="$GEMINI_KEY"
fi

if [ ! -z "$YOUTUBE_KEY" ]; then
    railway variables set YOUTUBE_API_KEY="$YOUTUBE_KEY"
fi

if [ ! -z "$DISCORD_URL" ]; then
    railway variables set DISCORD_WEBHOOK_URL="$DISCORD_URL"
fi

# Additional environment variables
railway variables set PYTHONPATH="/app"
railway variables set PORT="8000"
railway variables set HOST="0.0.0.0"

# Deploy
echo "🚀 Deploying application..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at the Railway-provided URL"