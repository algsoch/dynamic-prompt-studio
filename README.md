# Dynamic Prompt Template Studio

An advanced full-stack application for generating dynamic prompt templates and curating educational content using AI and YouTube analytics.

## Features

### 🎯 Core Functionality
- **Dynamic Prompt Generation**: Creates adaptive prompt templates for any learning topic
- **AI-Powered Content Curation**: Uses Gemini AI to generate educational content recommendations
- **YouTube Analytics**: Searches and analyzes up to 60 educational videos with advanced metrics
- **API Quota Tracking**: Real-time monitoring of API usage and limits
- **Copy-to-Clipboard**: Easy prompt sharing and usage

### 📊 Analytics & Visualizations
- Video difficulty distribution charts
- Top educational channels analysis
- Quality scoring algorithm
- Engagement rate calculations
- Comprehensive video metadata

### 🎨 User Experience
- Responsive design for all devices
- Modern card-based interface
- Interactive charts and graphs
- Real-time updates and notifications
- Collapsible sections and tabbed navigation

### 🔧 Technical Features
- FastAPI backend with async operations
- RESTful API design
- Error handling and demo modes
- Modular service architecture
- Cross-browser compatibility

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for API calls

### Installation & Running

1. **Clone or download this project**
2. **Run the startup script:**
   ```bash
   # Windows
   start.bat
   ```
3. **Open your browser to:** `http://localhost:8000`

The startup script will:
- Create a virtual environment
- Install all dependencies
- Create a template .env file
- Start the FastAPI server

### API Keys (Optional)

For full functionality, add your API keys to `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
YT_API_KEY=your_youtube_api_key_here
```

**Without API keys:** The app works in demo mode with sample data.

## How to Use

### 1. Choose a Topic
- Enter any learning topic (e.g., "Machine Learning", "Web Development")
- Or click on quick topic suggestions
- Default demo: "Prompt Engineering"

### 2. Generate Dynamic Prompt
- Click "Generate Prompt" to create a customized template
- View prompt metadata (word count, focus areas, etc.)
- Copy the prompt for use in AI tools

### 3. Explore AI Responses
- **Gemini Tab**: See AI-generated content curation
- **YouTube Tab**: Analyze educational videos with metrics

### 4. Analyze Results
- View video analytics charts
- Browse sortable/filterable video table
- Export or share findings

## Project Structure

```
prompt/
├── backend/
│   ├── main.py              # FastAPI application
│   └── services/
│       ├── prompt_template.py    # Dynamic prompt generation
│       ├── gemini_service.py     # Gemini AI integration
│       └── youtube_service.py    # YouTube API integration
├── frontend/
│   ├── index.html           # Main UI
│   ├── styles.css           # Responsive styling
│   └── app.js              # Frontend logic
├── requirements.txt         # Python dependencies
├── start.bat               # Windows startup script
└── .env                    # API keys (create this)
```

## API Endpoints

- `GET /` - Serve frontend
- `POST /api/generate-prompt` - Generate dynamic prompt
- `POST /api/gemini/query` - Query Gemini AI
- `POST /api/youtube/search` - Search YouTube videos
- `GET /api/quotas` - Get API quota status
- `POST /api/update-keys` - Update API keys
- `GET /api/topics/examples` - Get example topics

## Key Technologies

- **Backend**: FastAPI, Python, AsyncIO
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **APIs**: Google Gemini AI, YouTube Data API v3
- **Charts**: Chart.js for data visualization
- **Styling**: Modern CSS with custom properties
- **Markdown**: Marked.js for content rendering

## Demo Features

Even without API keys, you can:
- Generate dynamic prompts for any topic
- See demo AI responses
- Explore sample YouTube analytics
- Test all UI features and interactions

## Educational Focus

The app applies the **Pareto Principle (80/20 rule)** to content curation:
- Identifies the top 20% of content that delivers 80% of learning value
- Focuses on practical, actionable educational resources
- Balances theory with real-world applications
- Includes quality metrics and difficulty levels

## Customization

### Adding New Topics
Edit the example topics in `backend/main.py`:
```python
examples = [
    "Your Custom Topic",
    "Another Topic",
    # ... more topics
]
```

### Modifying Prompt Templates
Customize the base template in `backend/services/prompt_template.py`

### Styling Changes
Update CSS variables in `frontend/styles.css` for easy theme customization

## Troubleshooting

### Common Issues

1. **Port 8000 already in use:**
   ```bash
   # Change port in start.bat
   python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

2. **Missing dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **API quota exceeded:**
   - Check quota status in the app
   - Wait for quota reset (daily)
   - Or use your own API keys

### Support

This is an educational project. For issues:
1. Check the browser console for errors
2. Verify API keys are correct (if using)
3. Ensure internet connection for API calls

## License

Built for educational and demonstration purposes. Feel free to modify and extend!

---

**Happy Learning! 🚀**