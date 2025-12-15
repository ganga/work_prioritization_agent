"""
Pydantic schemas for Unified Dashboard API
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import ItemSource, ItemStatus


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Integration credentials
class SlackCredentials(BaseModel):
    token: str
    workspace: Optional[str] = None


class GmailCredentials(BaseModel):
    credentials_json: str  # JSON string from OAuth flow


class JiraCredentials(BaseModel):
    url: str
    email: EmailStr
    api_token: str


# Unified Item schemas
class UnifiedItemCreate(BaseModel):
    source: ItemSource
    source_id: str
    title: str
    content: Optional[str] = None
    sender: Optional[str] = None
    deadline: Optional[datetime] = None
    is_important: bool = False
    tags: Optional[str] = None


class UnifiedItemUpdate(BaseModel):
    user_rank: Optional[int] = None
    status: Optional[ItemStatus] = None
    is_important: Optional[bool] = None
    is_starred: Optional[bool] = None
    deadline: Optional[datetime] = None
    tags: Optional[str] = None
    reminder_time: Optional[datetime] = None


class UnifiedItemResponse(BaseModel):
    id: int
    source: ItemSource
    source_id: str
    source_url: Optional[str]
    title: str
    content: Optional[str]
    sender: Optional[str]
    recipient: Optional[str]
    priority_score: float
    user_rank: Optional[int]
    tags: Optional[str]
    status: ItemStatus
    is_important: bool
    is_starred: bool
    deadline: Optional[datetime]
    reminder_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    source_created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UnifiedItemListResponse(BaseModel):
    items: List[UnifiedItemResponse]
    total: int
    unread_count: int
    important_count: int
    overdue_count: int


# Priority calculation
class PriorityFactors(BaseModel):
    keyword_weight: float = 0.3
    deadline_weight: float = 0.4
    sender_weight: float = 0.2
    user_interaction_weight: float = 0.1


# Reminder schemas
class ReminderCreate(BaseModel):
    item_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    reminder_time: datetime


class ReminderResponse(BaseModel):
    id: int
    item_id: Optional[int]
    title: str
    description: Optional[str]
    reminder_time: datetime
    is_sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dashboard stats
class DashboardStats(BaseModel):
    total_items: int
    unread_items: int
    important_items: int
    overdue_items: int
    items_by_source: dict
    upcoming_deadlines: List[UnifiedItemResponse]
    recent_updates: List[UnifiedItemResponse]
