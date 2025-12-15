"""
Prioritization Service - Calculates priority scores for unified items
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from models import UnifiedItem, ItemSource
import re


class PrioritizationService:
    # Important keywords that increase priority
    IMPORTANT_KEYWORDS = [
        "urgent", "asap", "deadline", "important", "critical", "action required",
        "please review", "need your input", "blocking", "priority", "meeting",
        "action items", "follow up", "review needed", "approval needed"
    ]
    
    # Important senders (can be customized per user)
    IMPORTANT_SENDERS = [
        "manager", "director", "ceo", "cto", "vp", "lead"
    ]
    
    def calculate_priority_score(
        self,
        item: UnifiedItem,
        keyword_weight: float = 0.3,
        deadline_weight: float = 0.4,
        sender_weight: float = 0.2,
        user_interaction_weight: float = 0.1
    ) -> float:
        """
        Calculate priority score (0-10) based on multiple factors
        """
        score = 0.0
        text_content = f"{item.title} {item.content or ''}".lower()
        
        # 1. Keyword matching
        keyword_score = 0.0
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in text_content:
                keyword_score += 1.0
        
        keyword_score = min(keyword_score / len(self.IMPORTANT_KEYWORDS) * 10, 10.0)
        score += keyword_score * keyword_weight
        
        # 2. Deadline proximity
        deadline_score = 0.0
        if item.deadline:
            now = datetime.utcnow()
            time_diff = item.deadline - now
            
            if time_diff.total_seconds() < 0:
                deadline_score = 10.0  # Overdue
            elif time_diff.days == 0:
                deadline_score = 9.0  # Due today
            elif time_diff.days <= 1:
                deadline_score = 8.0
            elif time_diff.days <= 3:
                deadline_score = 6.0
            elif time_diff.days <= 7:
                deadline_score = 4.0
            elif time_diff.days <= 14:
                deadline_score = 2.0
        
        score += deadline_score * deadline_weight
        
        # 3. Sender importance
        sender_score = 0.0
        if item.sender:
            sender_lower = item.sender.lower()
            for important_sender in self.IMPORTANT_SENDERS:
                if important_sender in sender_lower:
                    sender_score = 5.0
                    break
        
        score += sender_score * sender_weight
        
        # 4. User interactions (starred, important flag)
        interaction_score = 0.0
        if item.is_starred:
            interaction_score += 5.0
        if item.is_important:
            interaction_score += 5.0
        if item.user_rank:
            # User ranking (1-10) contributes to score
            interaction_score += (11 - item.user_rank)  # Invert so 1 = highest
        
        score += min(interaction_score, 10.0) * user_interaction_weight
        
        # 5. Source-specific scoring
        source_score = 0.0
        if item.source == ItemSource.JIRA:
            # Jira items are often more actionable
            source_score = 3.0
        elif item.source == ItemSource.EMAIL:
            # Emails might be less urgent
            source_score = 2.0
        elif item.source == ItemSource.SLACK:
            # Slack messages are often quick updates
            source_score = 1.0
        
        score += source_score * 0.1
        
        # 6. Recency (newer items might be more relevant)
        if item.source_created_at:
            days_old = (datetime.utcnow() - item.source_created_at).days
            if days_old == 0:
                recency_score = 2.0
            elif days_old <= 1:
                recency_score = 1.5
            elif days_old <= 3:
                recency_score = 1.0
            else:
                recency_score = 0.5
            score += recency_score * 0.1
        
        # Cap at 10.0
        return min(score, 10.0)
    
    def extract_deadline_from_text(self, text: str) -> Optional[datetime]:
        """Extract deadline from text content"""
        if not text:
            return None
        
        patterns = [
            r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try different date formats
                    for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%B %d, %Y', '%b %d, %Y']:
                        try:
                            return datetime.strptime(match.strip(), fmt)
                        except:
                            continue
                except:
                    pass
        
        return None
    
    def is_important_by_keywords(self, text: str) -> bool:
        """Check if text contains important keywords"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in self.IMPORTANT_KEYWORDS:
            if keyword in text_lower:
                return True
        return False
