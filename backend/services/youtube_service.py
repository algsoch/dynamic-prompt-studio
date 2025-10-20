import os
import httpx
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import json

class YouTubeService:
    """Service for interacting with YouTube Data API v3"""
    
    def __init__(self):
        self.api_key = os.getenv("YT_API_KEY")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.quota_used = 0
        self.quota_limit = 10000  # Default daily quota
        self.requests_made = 0
    
    def update_api_key(self, api_key: str):
        """Update the YouTube API key"""
        self.api_key = api_key
    
    async def search_videos(
        self, 
        topic: str, 
        api_key: Optional[str] = None, 
        max_results: int = 60
    ) -> Dict[str, Any]:
        """Search for YouTube videos related to the topic"""
        
        # Use provided API key if available
        working_key = api_key if api_key else self.api_key
        
        if not working_key:
            return self._get_demo_videos(topic, max_results)
        
        try:
            videos = []
            search_queries = self._generate_search_queries(topic)
            results_per_query = max(1, max_results // len(search_queries))
            
            async with httpx.AsyncClient() as client:
                for query in search_queries:
                    batch = await self._search_batch(
                        client, query, working_key, results_per_query
                    )
                    videos.extend(batch)
                    
                    if len(videos) >= max_results:
                        break
            
            # Get detailed video information
            video_details = await self._get_video_details(videos[:max_results], working_key)
            
            # Analyze and sort videos
            analyzed_videos = self._analyze_videos(video_details, topic)
            
            return {
                "videos": analyzed_videos,
                "total_found": len(analyzed_videos),
                "topic": topic,
                "search_queries_used": search_queries,
                "quota_cost": self._calculate_quota_cost(len(analyzed_videos)),
                "analytics": self._generate_analytics(analyzed_videos),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Error searching YouTube: {str(e)}",
                "demo_data": self._get_demo_videos(topic, max_results),
                "success": False
            }
    
    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate multiple search queries for comprehensive results"""
        base_queries = [
            f"{topic} tutorial",
            f"{topic} guide",
            f"{topic} explained",
            f"{topic} course",
            f"{topic} fundamentals",
            f"{topic} advanced",
            f"{topic} project",
            f"{topic} best practices",
            f"learn {topic}",
            f"{topic} step by step"
        ]
        
        # Add topic-specific queries
        topic_lower = topic.lower()
        if "programming" in topic_lower or "coding" in topic_lower:
            base_queries.extend([
                f"{topic} for beginners",
                f"{topic} examples",
                f"{topic} interview questions"
            ])
        elif "data" in topic_lower:
            base_queries.extend([
                f"{topic} analysis",
                f"{topic} visualization",
                f"{topic} with python"
            ])
        
        return base_queries[:8]  # Limit to 8 queries to manage API usage
    
    async def _search_batch(
        self, 
        client: httpx.AsyncClient, 
        query: str, 
        api_key: str, 
        max_results: int
    ) -> List[Dict]:
        """Search for a batch of videos with a specific query"""
        
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max_results, 50),  # API limit
            "order": "relevance",
            "videoDuration": "medium",  # 4-20 minutes
            "key": api_key
        }
        
        response = await client.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        
        data = response.json()
        self.quota_used += 100  # Search costs 100 quota units
        self.requests_made += 1
        
        return data.get("items", [])
    
    async def _get_video_details(self, videos: List[Dict], api_key: str) -> List[Dict]:
        """Get detailed information for videos"""
        if not videos:
            return []
        
        video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
        
        if not video_ids:
            return []
        
        # Split into batches of 50 (API limit)
        batches = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
        all_details = []
        
        async with httpx.AsyncClient() as client:
            for batch in batches:
                params = {
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(batch),
                    "key": api_key
                }
                
                response = await client.get(f"{self.base_url}/videos", params=params)
                response.raise_for_status()
                
                data = response.json()
                all_details.extend(data.get("items", []))
                self.quota_used += 1  # Videos list costs 1 quota unit per request
        
        return all_details
    
    def _analyze_videos(self, videos: List[Dict], topic: str) -> List[Dict]:
        """Analyze and score videos based on quality metrics"""
        analyzed = []
        
        for video in videos:
            try:
                snippet = video.get("snippet", {})
                stats = video.get("statistics", {})
                content_details = video.get("contentDetails", {})
                
                # Extract metrics
                view_count = int(stats.get("viewCount", 0))
                like_count = int(stats.get("likeCount", 0))
                comment_count = int(stats.get("commentCount", 0))
                
                # Parse duration
                duration = self._parse_duration(content_details.get("duration", "PT0S"))
                
                # Calculate publish date
                published_at = datetime.fromisoformat(
                    snippet.get("publishedAt", "").replace("Z", "+00:00")
                )
                days_old = (datetime.now(published_at.tzinfo) - published_at).days
                
                # Calculate quality score
                quality_score = self._calculate_quality_score(
                    view_count, like_count, comment_count, days_old, duration, snippet.get("title", ""), topic
                )
                
                analyzed_video = {
                    "id": video["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200] + "...",
                    "channel_title": snippet.get("channelTitle", ""),
                    "published_at": published_at.isoformat(),
                    "duration": duration,
                    "duration_formatted": self._format_duration(duration),
                    "view_count": view_count,
                    "like_count": like_count,
                    "comment_count": comment_count,
                    "days_old": days_old,
                    "quality_score": quality_score,
                    "difficulty_level": self._determine_difficulty(snippet.get("title", ""), snippet.get("description", "")),
                    "url": f"https://www.youtube.com/watch?v={video['id']}",
                    "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                    "engagement_rate": self._calculate_engagement_rate(view_count, like_count, comment_count),
                    "relevance_score": self._calculate_relevance_score(snippet.get("title", ""), topic)
                }
                
                analyzed.append(analyzed_video)
                
            except Exception as e:
                print(f"Error analyzing video: {e}")
                continue
        
        # Sort by quality score
        analyzed.sort(key=lambda x: x["quality_score"], reverse=True)
        
        return analyzed
    
    def _calculate_quality_score(
        self, 
        views: int, 
        likes: int, 
        comments: int, 
        days_old: int, 
        duration: int, 
        title: str, 
        topic: str
    ) -> float:
        """Calculate a quality score for the video"""
        score = 0.0
        
        # View count score (logarithmic scale)
        if views > 0:
            score += min(10, (views / 1000) ** 0.5)
        
        # Engagement score
        if views > 0:
            like_ratio = likes / views if views > 0 else 0
            comment_ratio = comments / views if views > 0 else 0
            score += (like_ratio * 1000) + (comment_ratio * 5000)
        
        # Recency bonus (prefer newer content)
        if days_old < 365:
            score += (365 - days_old) / 365 * 2
        
        # Duration preference (10-30 minutes ideal)
        if 600 <= duration <= 1800:  # 10-30 minutes
            score += 2
        elif 300 <= duration <= 3600:  # 5-60 minutes
            score += 1
        
        # Title relevance
        title_lower = title.lower()
        topic_lower = topic.lower()
        if topic_lower in title_lower:
            score += 3
        
        # Educational keywords bonus
        educational_keywords = ["tutorial", "guide", "course", "learn", "explained", "fundamentals", "beginner"]
        for keyword in educational_keywords:
            if keyword in title_lower:
                score += 1
                break
        
        return round(score, 2)
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse YouTube duration format (PT1H2M3S) to seconds"""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _determine_difficulty(self, title: str, description: str) -> str:
        """Determine difficulty level based on title and description"""
        content = (title + " " + description).lower()
        
        beginner_keywords = ["beginner", "introduction", "basics", "getting started", "101", "fundamentals"]
        advanced_keywords = ["advanced", "expert", "master", "professional", "deep dive", "complex"]
        
        beginner_count = sum(1 for keyword in beginner_keywords if keyword in content)
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in content)
        
        if beginner_count > advanced_count:
            return "Beginner"
        elif advanced_count > beginner_count:
            return "Advanced"
        else:
            return "Intermediate"
    
    def _calculate_engagement_rate(self, views: int, likes: int, comments: int) -> float:
        """Calculate engagement rate"""
        if views == 0:
            return 0.0
        
        engagement = (likes + comments) / views * 100
        return round(engagement, 3)
    
    def _calculate_relevance_score(self, title: str, topic: str) -> float:
        """Calculate how relevant the video is to the topic"""
        title_lower = title.lower()
        topic_words = topic.lower().split()
        
        relevance = 0.0
        for word in topic_words:
            if word in title_lower:
                relevance += 1
        
        return relevance / len(topic_words) if topic_words else 0.0
    
    def _calculate_quota_cost(self, video_count: int) -> int:
        """Calculate the quota cost for the operation"""
        search_cost = 100 * 8  # 8 search queries
        video_details_cost = (video_count // 50 + 1) * 1  # Video details requests
        return search_cost + video_details_cost
    
    def _generate_analytics(self, videos: List[Dict]) -> Dict[str, Any]:
        """Generate analytics for the video collection"""
        if not videos:
            return {}
        
        total_views = sum(v["view_count"] for v in videos)
        total_likes = sum(v["like_count"] for v in videos)
        total_duration = sum(v["duration"] for v in videos)
        
        difficulty_distribution = {}
        for video in videos:
            level = video["difficulty_level"]
            difficulty_distribution[level] = difficulty_distribution.get(level, 0) + 1
        
        return {
            "total_videos": len(videos),
            "total_views": total_views,
            "total_likes": total_likes,
            "average_views": total_views // len(videos) if videos else 0,
            "average_duration": total_duration // len(videos) if videos else 0,
            "total_watch_time_hours": round(total_duration / 3600, 1),
            "difficulty_distribution": difficulty_distribution,
            "top_channels": self._get_top_channels(videos),
            "average_quality_score": round(sum(v["quality_score"] for v in videos) / len(videos), 2)
        }
    
    def _get_top_channels(self, videos: List[Dict]) -> List[Dict]:
        """Get top channels by video count"""
        channel_counts = {}
        for video in videos:
            channel = video["channel_title"]
            if channel:
                channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        sorted_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": name, "count": count} for name, count in sorted_channels[:5]]
    
    def _get_demo_videos(self, topic: str, max_results: int) -> Dict[str, Any]:
        """Generate demo video data when API is not available"""
        demo_videos = []
        
        for i in range(min(max_results, 10)):  # Limit demo to 10 videos
            demo_videos.append({
                "id": f"demo_{i+1}",
                "title": f"{topic} Tutorial #{i+1} - Complete Guide",
                "description": f"This is a comprehensive tutorial covering {topic} fundamentals and practical applications. Perfect for learners at all levels.",
                "channel_title": f"Educational Channel {i+1}",
                "published_at": (datetime.now() - timedelta(days=i*30)).isoformat(),
                "duration": 1200 + (i * 300),
                "duration_formatted": f"{20 + i*5}:00",
                "view_count": 50000 - (i * 5000),
                "like_count": 2000 - (i * 200),
                "comment_count": 150 - (i * 15),
                "days_old": i * 30,
                "quality_score": 8.5 - (i * 0.3),
                "difficulty_level": ["Beginner", "Intermediate", "Advanced"][i % 3],
                "url": f"https://www.youtube.com/watch?v=demo_{i+1}",
                "thumbnail": f"https://img.youtube.com/vi/demo_{i+1}/medium.jpg",
                "engagement_rate": 4.2 - (i * 0.2),
                "relevance_score": 0.9 - (i * 0.05)
            })
        
        return {
            "videos": demo_videos,
            "total_found": len(demo_videos),
            "topic": topic,
            "is_demo": True,
            "analytics": self._generate_analytics(demo_videos),
            "note": "This is demo data. Provide your YouTube API key for real video search results.",
            "success": True
        }
    
    async def get_quota_info(self) -> Dict[str, Any]:
        """Get current quota information"""
        return {
            "service": "YouTube Data API",
            "quota_used": self.quota_used,
            "quota_limit": self.quota_limit,
            "quota_remaining": max(0, self.quota_limit - self.quota_used),
            "percentage_used": (self.quota_used / self.quota_limit) * 100,
            "requests_made": self.requests_made,
            "api_key_configured": bool(self.api_key),
            "last_updated": datetime.now().isoformat(),
            "quota_type": "Simulated - Default limit set to 10,000 units per day",
            "note": "These are simulated quotas. Real YouTube API quotas are managed by Google Cloud Console and vary by project."
        }