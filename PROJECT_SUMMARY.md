# 📊 Dynamic Prompt Studio - Project Summary

## Project Overview

**Dynamic Prompt Studio** is a full-stack AI-powered educational content curation platform that:
- Generates dynamic prompt templates for any learning topic
- Uses Google Gemini AI for intelligent content recommendations
- Analyzes YouTube videos with advanced educational metrics
- Tracks API usage and quota limits
- Logs all activity to Discord webhooks

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **AI Integration**: Google Gemini API
- **YouTube API**: YouTube Data API v3
- **Async Operations**: AsyncIO for concurrent requests
- **Environment**: Docker containerized

### Frontend
- **Pure JavaScript** (No frameworks)
- **Chart.js**: Data visualization
- **Marked.js**: Markdown rendering
- **Responsive CSS**: Mobile-first design
- **Font Awesome**: Icons

### Deployment
- **Platform**: Render (Free Tier)
- **Container**: Docker
- **Auto-deploy**: GitHub integration
- **Keep-Alive**: GitHub Actions workflow

## Key Features

1. **Dynamic Prompt Generation**
   - Creates customized prompts based on topic
   - Applies 80/20 (Pareto) principle
   - Includes metadata (word count, focus areas, etc.)

2. **AI-Powered Curation**
   - Gemini AI integration
   - Demo mode when no API key
   - Smart content recommendations

3. **YouTube Analytics**
   - Searches up to 60 educational videos
   - Quality scoring algorithm
   - Difficulty level classification
   - Engagement rate calculations
   - Channel analytics

4. **Real-time Monitoring**
   - Discord webhook logging
   - API quota tracking
   - Health check endpoints
   - Smart request filtering

## Project Structure

```
dynamic-prompt-studio/
├── backend/
│   ├── main.py                    # FastAPI application
│   └── services/
│       ├── prompt_template.py     # Prompt generation logic
│       ├── gemini_service.py      # Gemini AI integration
│       ├── youtube_service.py     # YouTube API integration
│       └── discord_service.py     # Discord webhook logging
├── frontend/
│   ├── index.html                 # Main UI
│   ├── app.js                     # Frontend logic
│   └── styles.css                 # Responsive styling
├── deploy/
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── railway.sh                # Railway deployment
│   ├── render.sh                 # Render deployment
│   └── docker.sh                 # Docker deployment
├── .github/
│   └── workflows/
│       └── keep-alive.yml        # Render keep-alive automation
├── Dockerfile                     # Container configuration
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Local development
├── .env                          # Environment variables
└── README.md                     # Documentation
```

## Current Issue & Fix

### Problem
App was **stuck at "Generating dynamic prompt template..."** on Render deployment.

### Root Causes
1. Auto-generation triggered on page load during cold start
2. No timeout handling for API requests
3. Render free tier cold starts take 30-60 seconds

### Solutions Implemented
1. ✅ Removed auto-generation on page load
2. ✅ Added 30-60 second timeouts to all API calls
3. ✅ Better error handling with user-friendly messages
4. ✅ Backend health check on startup
5. ✅ Graceful failure modes for slow responses

### Files Modified
- `frontend/app.js` - All API call functions updated with timeouts and error handling

## Environment Variables

### Required
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### Optional (For Full Functionality)
```env
GEMINI_API_KEY=your_gemini_api_key_here
YT_API_KEY=your_youtube_api_key_here
```

### System Variables (Render)
```env
PYTHONPATH=/app
PORT=8000
HOST=0.0.0.0
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve frontend |
| `/api/health` | GET | Health check |
| `/api/generate-prompt` | POST | Generate prompt template |
| `/api/gemini/query` | POST | Query Gemini AI |
| `/api/youtube/search` | POST | Search YouTube videos |
| `/api/quotas` | GET | Get API quota status |
| `/api/update-keys` | POST | Update API keys |
| `/api/topics/examples` | GET | Get example topics |

## Deployment Status

### Current Deployment
- **Platform**: Render
- **Status**: Live & Deployed
- **URL**: [Your Render URL]
- **Tier**: Free

### Known Behavior
- First request after 15min inactivity: 30-60 seconds (cold start)
- Subsequent requests: < 1 second
- Keep-alive workflow prevents sleeping (pings every 14min)

## How to Use

### For Users
1. Open the app in browser
2. Enter a learning topic (or select from quick topics)
3. Click "Generate Prompt" button
4. Explore AI responses and YouTube analytics
5. Optional: Add API keys for full functionality

### For Developers

#### Local Development
```bash
# Start with Docker Compose
docker-compose up

# Or start manually
python backend/main.py
# Open http://localhost:8000
```

#### Deploy to Render
```bash
git add .
git commit -m "Update deployment"
git push origin main
# Render auto-deploys
```

## Testing Checklist

After deployment, verify:
- [ ] Page loads instantly (no infinite spinner)
- [ ] Default topic appears in input
- [ ] Generate Prompt button works
- [ ] Error messages appear on timeout
- [ ] Toast notifications work
- [ ] Quota cards load or fail gracefully
- [ ] All API endpoints respond correctly
- [ ] Discord webhook receives logs

## Monitoring

### Discord Webhook Logs
- Visitor tracking
- API request logging
- Error notifications
- Smart filtering (excludes automated bots)

### Render Dashboard
- Resource usage
- Deployment logs
- Request logs
- Performance metrics

## Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Save/bookmark prompts
- [ ] Export functionality
- [ ] More AI model integrations
- [ ] Advanced filtering options
- [ ] Custom prompt templates

### Performance Improvements
- [ ] Redis caching
- [ ] Database for user data
- [ ] CDN for static assets
- [ ] Background job processing

## Troubleshooting

See `TROUBLESHOOTING.md` for detailed guide on:
- Cold start issues
- Timeout handling
- Error messages
- Deployment problems
- Monitoring setup

## Documentation

- `README.md` - User guide and features
- `DEPLOYMENT.md` - Deployment instructions
- `TROUBLESHOOTING.md` - Issue resolution guide
- This file - Project overview

## Credits

**Built by**: Vicky Kumar (@algsoch)
**Repository**: github.com/algsoch/dynamic-prompt-studio
**Version**: 1.0.1
**Last Updated**: November 29, 2025

## License

Educational and demonstration purposes. Free to modify and extend.
