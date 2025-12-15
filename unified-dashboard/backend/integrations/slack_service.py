"""
Slack Integration Service
"""
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict, Optional
from datetime import datetime
import re


class SlackService:
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def get_channels(self) -> List[Dict]:
        """Get all channels the user has access to"""
        try:
            response = self.client.conversations_list(types="public_channel,private_channel")
            return response["channels"]
        except SlackApiError as e:
            print(f"Error fetching channels: {e}")
            return []
    
    def get_messages(self, channel_id: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a channel"""
        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )
            messages = []
            for msg in response["messages"]:
                # Skip bot messages and threads for now
                if msg.get("subtype") or msg.get("thread_ts"):
                    continue
                
                messages.append({
                    "id": msg["ts"],
                    "text": msg.get("text", ""),
                    "user": msg.get("user", "unknown"),
                    "channel": channel_id,
                    "timestamp": datetime.fromtimestamp(float(msg["ts"])),
                    "url": f"https://slack.com/archives/{channel_id}/p{msg['ts'].replace('.', '')}"
                })
            return messages
        except SlackApiError as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def get_mentions(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get messages where user is mentioned"""
        try:
            # Search for messages mentioning the user
            query = f"<@{user_id}>"
            response = self.client.search_messages(query=query, count=limit)
            
            messages = []
            for match in response.get("messages", {}).get("matches", []):
                messages.append({
                    "id": match["ts"],
                    "text": match.get("text", ""),
                    "user": match.get("user", "unknown"),
                    "channel": match.get("channel", {}).get("name", "unknown"),
                    "timestamp": datetime.fromtimestamp(float(match["ts"])),
                    "url": match.get("permalink", "")
                })
            return messages
        except SlackApiError as e:
            print(f"Error fetching mentions: {e}")
            return []
    
    def get_direct_messages(self, limit: int = 50) -> List[Dict]:
        """Get direct messages"""
        try:
            # Get DMs
            response = self.client.conversations_list(types="im")
            messages = []
            
            for channel in response["channels"]:
                channel_messages = self.get_messages(channel["id"], limit=10)
                messages.extend(channel_messages)
            
            return sorted(messages, key=lambda x: x["timestamp"], reverse=True)[:limit]
        except SlackApiError as e:
            print(f"Error fetching DMs: {e}")
            return []
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        try:
            response = self.client.users_info(user=user_id)
            return response["user"]
        except SlackApiError:
            return None
    
    def extract_important_keywords(self, text: str) -> List[str]:
        """Extract important keywords from message text"""
        important_keywords = [
            "urgent", "asap", "deadline", "important", "critical", "action required",
            "please review", "need your input", "blocking", "priority"
        ]
        found = []
        text_lower = text.lower()
        for keyword in important_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found
