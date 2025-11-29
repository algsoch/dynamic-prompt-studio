import os
import httpx
import json
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio
from urllib.parse import urlparse

class DiscordWebhookService:
    """Service for sending logs and notifications to Discord via webhook"""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
        
    async def send_request_log(
        self, 
        method: str, 
        endpoint: str, 
        user_ip: str, 
        user_agent: str,
        status_code: int,
        response_data: Any = None,
        request_data: Any = None,
        processing_time: float = 0.0
    ):
        """Send request log to Discord webhook"""
        if not self.enabled:
            return
            
        try:
            # Create embed for the request log
            embed = {
                "title": f"🌐 API Request - {method} {endpoint}",
                "color": self._get_status_color(status_code),
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "📍 Endpoint",
                        "value": f"`{method} {endpoint}`",
                        "inline": True
                    },
                    {
                        "name": "🔢 Status Code",
                        "value": f"`{status_code}`",
                        "inline": True
                    },
                    {
                        "name": "⏱️ Processing Time",
                        "value": f"`{processing_time:.3f}s`",
                        "inline": True
                    },
                    {
                        "name": "🌍 Client IP",
                        "value": f"`{user_ip}`",
                        "inline": True
                    },
                    {
                        "name": "🔧 User Agent",
                        "value": f"`{user_agent[:100]}...`" if len(user_agent) > 100 else f"`{user_agent}`",
                        "inline": False
                    }
                ]
            }
            
            # Add request data if present
            if request_data:
                request_str = self._format_data(request_data)
                if request_str:
                    embed["fields"].append({
                        "name": "📤 Request Data",
                        "value": f"```json\n{request_str}\n```",
                        "inline": False
                    })
            
            # Add response data if present (truncated for Discord limits)
            if response_data:
                response_str = self._format_data(response_data, max_length=800)
                if response_str:
                    embed["fields"].append({
                        "name": "📥 Response Data",
                        "value": f"```json\n{response_str}\n```",
                        "inline": False
                    })
            
            payload = {
                "embeds": [embed],
                "username": "Prompt Template API Bot",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
            }
            
            await self._send_webhook(payload)
            
        except Exception as e:
            print(f"Error sending Discord webhook: {e}")
    
    async def send_visitor_log(self, user_ip: str, user_agent: str, referer: str = None):
        """Send visitor log to Discord webhook"""
        if not self.enabled:
            return
            
        try:
            embed = {
                "title": "👋 New Visitor",
                "color": 0x00ff00,  # Green
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "🌍 IP Address",
                        "value": f"`{user_ip}`",
                        "inline": True
                    },
                    {
                        "name": "⏰ Visit Time",
                        "value": f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                        "inline": True
                    },
                    {
                        "name": "🔧 User Agent",
                        "value": f"`{user_agent[:150]}...`" if len(user_agent) > 150 else f"`{user_agent}`",
                        "inline": False
                    }
                ]
            }
            
            if referer:
                embed["fields"].append({
                    "name": "🔗 Referer",
                    "value": f"`{referer}`",
                    "inline": False
                })
            
            payload = {
                "embeds": [embed],
                "username": "Prompt Template Visitor Tracker",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/1.png"
            }
            
            await self._send_webhook(payload)
            
        except Exception as e:
            print(f"Error sending visitor webhook: {e}")
    
    async def send_error_log(self, error: str, endpoint: str, user_ip: str, traceback: str = None):
        """Send error log to Discord webhook"""
        if not self.enabled:
            return
            
        try:
            embed = {
                "title": "🚨 Application Error",
                "color": 0xff0000,  # Red
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {
                        "name": "❌ Error",
                        "value": f"`{error[:500]}...`" if len(error) > 500 else f"`{error}`",
                        "inline": False
                    },
                    {
                        "name": "📍 Endpoint",
                        "value": f"`{endpoint}`",
                        "inline": True
                    },
                    {
                        "name": "🌍 Client IP",
                        "value": f"`{user_ip}`",
                        "inline": True
                    }
                ]
            }
            
            if traceback:
                embed["fields"].append({
                    "name": "📋 Traceback",
                    "value": f"```python\n{traceback[:1000]}...\n```" if len(traceback) > 1000 else f"```python\n{traceback}\n```",
                    "inline": False
                })
            
            payload = {
                "embeds": [embed],
                "username": "Prompt Template Error Bot",
                "avatar_url": "https://cdn.discordapp.com/embed/avatars/2.png"
            }
            
            await self._send_webhook(payload)
            
        except Exception as e:
            print(f"Error sending error webhook: {e}")
    
    def _get_status_color(self, status_code: int) -> int:
        """Get Discord embed color based on HTTP status code"""
        if 200 <= status_code < 300:
            return 0x00ff00  # Green
        elif 300 <= status_code < 400:
            return 0xffff00  # Yellow
        elif 400 <= status_code < 500:
            return 0xff8800  # Orange
        else:
            return 0xff0000  # Red
    
    def _format_data(self, data: Any, max_length: int = 1500) -> str:
        """Format data for Discord display"""
        try:
            if isinstance(data, dict):
                # Remove sensitive data
                cleaned_data = self._clean_sensitive_data(data)
                formatted = json.dumps(cleaned_data, indent=2, ensure_ascii=False)
            elif isinstance(data, str):
                formatted = data
            else:
                formatted = str(data)
            
            if len(formatted) > max_length:
                return formatted[:max_length] + "..."
            return formatted
        except Exception:
            return str(data)[:max_length]
    
    def _clean_sensitive_data(self, data: dict) -> dict:
        """Remove sensitive information from data"""
        sensitive_keys = ['api_key', 'password', 'token', 'secret', 'key']
        cleaned = {}
        
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                cleaned[key] = "[REDACTED]" if value else None
            elif isinstance(value, dict):
                cleaned[key] = self._clean_sensitive_data(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    async def _send_webhook(self, payload: dict):
        """Send payload to Discord webhook (non-blocking with short timeout)"""
        try:
            # Use a short timeout to avoid blocking requests
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
        except httpx.TimeoutException:
            print("Discord webhook timeout (non-critical, continuing)")
        except httpx.HTTPStatusError as e:
            print(f"Discord webhook HTTP error: {e.response.status_code} (non-critical)")
        except Exception as e:
            print(f"Discord webhook error: {e} (non-critical)")