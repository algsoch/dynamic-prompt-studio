import os
import google.generativeai as genai
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.0-flash-exp"
        self.client = None
        self.quota_used = 0
        self.quota_limit = 1000  # Default quota limit
        
        if self.api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Gemini client"""
        try:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        except Exception as e:
            print(f"Error initializing Gemini client: {e}")
            self.client = None
    
    def update_api_key(self, api_key: str):
        """Update the API key and reinitialize client"""
        self.api_key = api_key
        self._initialize_client()
    
    async def query(self, prompt: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Query the Gemini API with the given prompt"""
        
        # Use provided API key if available
        if api_key and api_key != self.api_key:
            temp_key = self.api_key
            self.update_api_key(api_key)
            
        if not self.client:
            return {
                "error": "Gemini API not configured. Please provide a valid API key.",
                "demo_response": self._get_demo_response(prompt)
            }
        
        try:
            # Generate content using Gemini
            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                    top_p=0.9,
                    top_k=40
                )
            )
            
            self.quota_used += 1
            
            return {
                "response": response.text,
                "model": self.model_name,
                "tokens_used": len(response.text.split()),
                "timestamp": datetime.now().isoformat(),
                "quota_used": self.quota_used,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Error querying Gemini API: {str(e)}",
                "demo_response": self._get_demo_response(prompt),
                "success": False
            }
        
        finally:
            # Restore original API key if temporary key was used
            if api_key and api_key != temp_key:
                self.update_api_key(temp_key)
    
    def _get_demo_response(self, prompt: str) -> Dict[str, Any]:
        """Generate a demo response when API is not available"""
        topic = "the requested topic"
        
        # Extract topic from prompt if possible
        if "topic:" in prompt.lower() or "topic **" in prompt.lower():
            lines = prompt.split('\n')
            for line in lines:
                if 'topic:' in line.lower() or 'topic **' in line.lower():
                    # Extract topic name
                    if '**' in line:
                        topic = line.split('**')[1].split('**')[0].strip()
                    else:
                        topic = line.split(':')[1].strip()
                    break
        
        demo_content = f"""# Demo Response for {topic}

## Top YouTube Video Recommendations

Here are carefully curated educational videos for **{topic}**:

### Beginner Level (40%)
1. **Introduction to {topic}: Complete Beginner's Guide**
   - Channel: TechEdu Academy
   - Duration: 25:30
   - Key Points: Fundamentals, basic concepts, getting started
   - Why Selected: Perfect entry point with clear explanations

2. **{topic} Explained Simply - Step by Step Tutorial**
   - Channel: Learn With Me
   - Duration: 18:45
   - Key Points: Practical examples, hands-on approach
   - Why Selected: Excellent for visual learners

### Intermediate Level (40%)
3. **Advanced {topic} Techniques and Best Practices**
   - Channel: Pro Developer
   - Duration: 32:15
   - Key Points: Industry standards, optimization tips
   - Why Selected: Bridges beginner to professional level

4. **Real-World {topic} Project Walkthrough**
   - Channel: Code Masters
   - Duration: 45:20
   - Key Points: Complete project, problem-solving
   - Why Selected: Practical application focus

### Advanced Level (20%)
5. **Expert-Level {topic} Strategies and Patterns**
   - Channel: Tech Experts
   - Duration: 28:10
   - Key Points: Advanced concepts, scalability
   - Why Selected: Cutting-edge techniques

*Note: This is a demo response. Connect your Gemini API key for full AI-powered content curation with 60 personalized video recommendations.*

## Key Learning Path
1. Start with fundamentals
2. Practice with tutorials
3. Build real projects
4. Explore advanced concepts
5. Stay updated with trends

**Estimated Learning Time**: 40-60 hours for comprehensive understanding
**Recommended Pace**: 5-7 videos per week with hands-on practice
"""
        
        return {
            "content": demo_content,
            "is_demo": True,
            "topic": topic,
            "video_count": 5,
            "note": "This is a demo response. Provide your Gemini API key for full functionality."
        }
    
    async def get_quota_info(self) -> Dict[str, Any]:
        """Get current quota information"""
        return {
            "service": "Gemini API",
            "quota_used": self.quota_used,
            "quota_limit": self.quota_limit,
            "quota_remaining": max(0, self.quota_limit - self.quota_used),
            "percentage_used": (self.quota_used / self.quota_limit) * 100,
            "api_key_configured": bool(self.api_key and self.client),
            "model": self.model_name,
            "last_updated": datetime.now().isoformat(),
            "quota_type": "Simulated - Default limit set to 1000 requests per day",
            "note": "These are simulated quotas. Real Gemini API quotas depend on your Google Cloud project settings."
        }