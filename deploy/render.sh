#!/bin/bash

# Deploy to Render
echo "🚀 Deploying to Render..."

echo "📋 To deploy to Render:"
echo "1. Go to https://render.com and sign up/login"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect your GitHub repository: https://github.com/algsoch/dynamic-prompt-studio"
echo "4. Configure the following settings:"
echo ""
echo "   🔧 Build & Deploy Settings:"
echo "   • Environment: Docker"
echo "   • Region: Choose closest to your users"
echo "   • Branch: main"
echo "   • Dockerfile Path: ./Dockerfile"
echo ""
echo "   ⚙️ Environment Variables:"
echo "   • GEMINI_API_KEY=your_gemini_api_key_here"
echo "   • YOUTUBE_API_KEY=your_youtube_api_key_here"
echo "   • DISCORD_WEBHOOK_URL=your_discord_webhook_url"
echo "   • PYTHONPATH=/app"
echo "   • PORT=8000"
echo ""
echo "   💰 Pricing:"
echo "   • Free tier: 750 hours/month (sleeps after 15min inactivity)"
echo "   • Starter: $7/month (always on)"
echo ""
echo "5. Click 'Create Web Service'"
echo "6. Wait for deployment to complete"
echo ""
echo "✅ Your app will be available at: https://your-app-name.onrender.com"

# Open Render in browser
if command -v xdg-open &> /dev/null; then
    xdg-open "https://render.com"
elif command -v open &> /dev/null; then
    open "https://render.com"
fi