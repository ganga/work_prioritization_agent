"""
Database models for Unified Dashboard
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class ItemSource(str, enum.Enum):
    SLACK = "slack"
    EMAIL = "email"
    JIRA = "jira"


class ItemStatus(str, enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Integration credentials (encrypted in production)
    slack_token = Column(String, nullable=True)
    slack_workspace = Column(String, nullable=True)
    gmail_credentials = Column(Text, nullable=True)  # JSON string
    jira_url = Column(String, nullable=True)
    jira_email = Column(String, nullable=True)
    jira_api_token = Column(String, nullable=True)
    
    unified_items = relationship("UnifiedItem", back_populates="user")


class UnifiedItem(Base):
    __tablename__ = "unified_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Source information
    source = Column(Enum(ItemSource), nullable=False)
    source_id = Column(String, nullable=False)  # Original ID from source
    source_url = Column(String, nullable=True)
    
    # Content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    sender = Column(String, nullable=True)
    recipient = Column(String, nullable=True)
    
    # Prioritization
    priority_score = Column(Float, default=0.0)  # Calculated priority score
    user_rank = Column(Integer, nullable=True)  # User-defined ranking
    tags = Column(String, nullable=True)  # Comma-separated tags
    
    # Status and tracking
    status = Column(Enum(ItemStatus), default=ItemStatus.UNREAD)
    is_important = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    
    # Deadline and reminders
    deadline = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    reminder_time = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_created_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="unified_items")
    updates = relationship("ItemUpdate", back_populates="item", cascade="all, delete-orphan")


class ItemUpdate(Base):
    __tablename__ = "item_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("unified_items.id"))
    
    update_type = Column(String, nullable=False)  # e.g., "status_change", "comment", "priority_change"
    update_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    item = relationship("UnifiedItem", back_populates="updates")


class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("unified_items.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reminder_time = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
