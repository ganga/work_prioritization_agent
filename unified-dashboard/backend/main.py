"""
Unified Dashboard API - Main FastAPI Application
Integrates Slack, Email (Gmail), and Jira into a single prioritized dashboard
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from jose import jwt
from passlib.context import CryptContext

from database import SessionLocal, engine, Base
from models import User, UnifiedItem, ItemUpdate, Reminder, ItemSource, ItemStatus
from schemas import (
    UserCreate, UserResponse, UnifiedItemResponse, UnifiedItemUpdate,
    UnifiedItemListResponse, DashboardStats, ReminderCreate, ReminderResponse,
    SlackCredentials, GmailCredentials, JiraCredentials, PriorityFactors
)
from integrations.slack_service import SlackService
from integrations.email_service import GmailService
from integrations.jira_service import JiraService
from services.prioritization import PrioritizationService

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Unified Dashboard API",
    description="A unified dashboard for Slack, Email, and Jira with prioritization and reminders",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
prioritization_service = PrioritizationService()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication helpers
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# Routes
@app.get("/")
async def root():
    return {
        "message": "Unified Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# Integration credentials
@app.post("/integrations/slack")
async def set_slack_credentials(
    credentials: SlackCredentials,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set Slack integration credentials"""
    current_user.slack_token = credentials.token
    current_user.slack_workspace = credentials.workspace
    db.commit()
    return {"message": "Slack credentials saved"}


@app.post("/integrations/gmail")
async def set_gmail_credentials(
    credentials: GmailCredentials,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set Gmail integration credentials"""
    current_user.gmail_credentials = credentials.credentials_json
    db.commit()
    return {"message": "Gmail credentials saved"}


@app.post("/integrations/jira")
async def set_jira_credentials(
    credentials: JiraCredentials,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set Jira integration credentials"""
    current_user.jira_url = credentials.url
    current_user.jira_email = credentials.email
    current_user.jira_api_token = credentials.api_token
    db.commit()
    return {"message": "Jira credentials saved"}


# Sync functions
async def sync_slack_items(user: User, db: Session):
    """Sync items from Slack"""
    if not user.slack_token:
        return
    
    try:
        slack_service = SlackService(user.slack_token)
        
        # Get mentions
        mentions = slack_service.get_mentions("current_user", limit=50)
        
        for mention in mentions:
            # Check if item already exists
            existing = db.query(UnifiedItem).filter(
                and_(
                    UnifiedItem.user_id == user.id,
                    UnifiedItem.source == ItemSource.SLACK,
                    UnifiedItem.source_id == mention["id"]
                )
            ).first()
            
            if not existing:
                item = UnifiedItem(
                    user_id=user.id,
                    source=ItemSource.SLACK,
                    source_id=mention["id"],
                    source_url=mention.get("url", ""),
                    title=f"Slack: {mention.get('channel', 'Direct Message')}",
                    content=mention.get("text", ""),
                    sender=mention.get("user", "Unknown"),
                    source_created_at=mention.get("timestamp"),
                    is_important=prioritization_service.is_important_by_keywords(mention.get("text", ""))
                )
                
                # Extract deadline if present
                deadline = prioritization_service.extract_deadline_from_text(mention.get("text", ""))
                if deadline:
                    item.deadline = deadline
                
                # Calculate priority
                item.priority_score = prioritization_service.calculate_priority_score(item)
                
                db.add(item)
        
        db.commit()
    except Exception as e:
        print(f"Error syncing Slack: {e}")


async def sync_email_items(user: User, db: Session):
    """Sync items from Gmail"""
    if not user.gmail_credentials:
        return
    
    try:
        gmail_service = GmailService(user.gmail_credentials)
        
        # Get unread and important emails
        emails = gmail_service.get_unread_emails(max_results=50)
        emails.extend(gmail_service.get_important_emails(max_results=20))
        
        for email in emails:
            # Check if item already exists
            existing = db.query(UnifiedItem).filter(
                and_(
                    UnifiedItem.user_id == user.id,
                    UnifiedItem.source == ItemSource.EMAIL,
                    UnifiedItem.source_id == email["id"]
                )
            ).first()
            
            if not existing:
                item = UnifiedItem(
                    user_id=user.id,
                    source=ItemSource.EMAIL,
                    source_id=email["id"],
                    source_url=email.get("url", ""),
                    title=email.get("subject", "No Subject"),
                    content=email.get("snippet", ""),
                    sender=email.get("sender", "Unknown"),
                    source_created_at=email.get("date"),
                    is_important="important" in email.get("labels", []) or "starred" in email.get("labels", [])
                )
                
                # Extract deadline
                deadline = prioritization_service.extract_deadline_from_text(
                    f"{email.get('subject', '')} {email.get('snippet', '')}"
                )
                if deadline:
                    item.deadline = deadline
                
                # Calculate priority
                item.priority_score = prioritization_service.calculate_priority_score(item)
                
                db.add(item)
        
        db.commit()
    except Exception as e:
        print(f"Error syncing Gmail: {e}")


async def sync_jira_items(user: User, db: Session):
    """Sync items from Jira"""
    if not user.jira_api_token or not user.jira_url:
        return
    
    try:
        jira_service = JiraService(user.jira_url, user.jira_email, user.jira_api_token)
        
        # Get various types of issues
        issues = jira_service.get_my_issues(max_results=50)
        issues.extend(jira_service.get_high_priority_issues(max_results=20))
        issues.extend(jira_service.get_issues_with_deadlines(max_results=20))
        
        for issue in issues:
            # Check if item already exists
            existing = db.query(UnifiedItem).filter(
                and_(
                    UnifiedItem.user_id == user.id,
                    UnifiedItem.source == ItemSource.JIRA,
                    UnifiedItem.source_id == issue["key"]
                )
            ).first()
            
            if not existing:
                item = UnifiedItem(
                    user_id=user.id,
                    source=ItemSource.JIRA,
                    source_id=issue["key"],
                    source_url=issue.get("url", ""),
                    title=f"Jira: {issue.get('summary', 'No Summary')}",
                    content=issue.get("description", ""),
                    sender=issue.get("reporter", "Unknown"),
                    source_created_at=issue.get("created"),
                    deadline=issue.get("due_date"),
                    is_important=issue.get("priority") in ["Highest", "High"]
                )
                
                # Calculate priority using Jira-specific logic
                item.priority_score = jira_service.calculate_priority_score(issue)
                
                db.add(item)
            else:
                # Update existing item
                existing.deadline = issue.get("due_date")
                existing.updated_at = datetime.utcnow()
                existing.priority_score = jira_service.calculate_priority_score(issue)
        
        db.commit()
    except Exception as e:
        print(f"Error syncing Jira: {e}")


@app.post("/sync")
async def sync_all(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync all integrations"""
    background_tasks.add_task(sync_slack_items, current_user, db)
    background_tasks.add_task(sync_email_items, current_user, db)
    background_tasks.add_task(sync_jira_items, current_user, db)
    
    return {"message": "Sync started in background"}


# Unified Items endpoints
@app.get("/items", response_model=UnifiedItemListResponse)
async def get_items(
    source: Optional[ItemSource] = None,
    status: Optional[ItemStatus] = None,
    important_only: bool = False,
    sort_by: str = "priority_score",  # priority_score, deadline, created_at, user_rank
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unified items with filtering and sorting"""
    query = db.query(UnifiedItem).filter(UnifiedItem.user_id == current_user.id)
    
    if source:
        query = query.filter(UnifiedItem.source == source)
    if status:
        query = query.filter(UnifiedItem.status == status)
    if important_only:
        query = query.filter(UnifiedItem.is_important == True)
    
    # Sorting
    if sort_by == "priority_score":
        query = query.order_by(UnifiedItem.priority_score.desc(), UnifiedItem.created_at.desc())
    elif sort_by == "deadline":
        query = query.order_by(
            UnifiedItem.deadline.asc().nullslast(),
            UnifiedItem.priority_score.desc()
        )
    elif sort_by == "user_rank":
        query = query.order_by(
            UnifiedItem.user_rank.asc().nullslast(),
            UnifiedItem.priority_score.desc()
        )
    else:
        query = query.order_by(UnifiedItem.created_at.desc())
    
    items = query.limit(limit).all()
    
    # Recalculate priorities
    for item in items:
        item.priority_score = prioritization_service.calculate_priority_score(item)
    
    db.commit()
    
    # Calculate stats
    unread_count = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.status == ItemStatus.UNREAD
        )
    ).count()
    
    important_count = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.is_important == True
        )
    ).count()
    
    overdue_count = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.deadline < datetime.utcnow(),
            UnifiedItem.status != ItemStatus.COMPLETED
        )
    ).count()
    
    return UnifiedItemListResponse(
        items=items,
        total=len(items),
        unread_count=unread_count,
        important_count=important_count,
        overdue_count=overdue_count
    )


@app.get("/items/{item_id}", response_model=UnifiedItemResponse)
async def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific item"""
    item = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.id == item_id,
            UnifiedItem.user_id == current_user.id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


@app.patch("/items/{item_id}", response_model=UnifiedItemResponse)
async def update_item(
    item_id: int,
    item_update: UnifiedItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item (rank, status, etc.)"""
    item = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.id == item_id,
            UnifiedItem.user_id == current_user.id
        )
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Update fields
    if item_update.user_rank is not None:
        item.user_rank = item_update.user_rank
    if item_update.status:
        item.status = item_update.status
    if item_update.is_important is not None:
        item.is_important = item_update.is_important
    if item_update.is_starred is not None:
        item.is_starred = item_update.is_starred
    if item_update.deadline is not None:
        item.deadline = item_update.deadline
    if item_update.tags:
        item.tags = item_update.tags
    if item_update.reminder_time:
        item.reminder_time = item_update.reminder_time
    
    # Recalculate priority
    item.priority_score = prioritization_service.calculate_priority_score(item)
    item.updated_at = datetime.utcnow()
    
    # Log update
    update = ItemUpdate(
        item_id=item.id,
        update_type="user_update",
        update_content=f"Updated by user"
    )
    db.add(update)
    
    db.commit()
    db.refresh(item)
    
    return item


@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    total_items = db.query(UnifiedItem).filter(UnifiedItem.user_id == current_user.id).count()
    unread_items = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.status == ItemStatus.UNREAD
        )
    ).count()
    important_items = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.is_important == True
        )
    ).count()
    overdue_items = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.deadline < datetime.utcnow(),
            UnifiedItem.status != ItemStatus.COMPLETED
        )
    ).count()
    
    # Items by source
    items_by_source = {}
    for source in ItemSource:
        count = db.query(UnifiedItem).filter(
            and_(
                UnifiedItem.user_id == current_user.id,
                UnifiedItem.source == source
            )
        ).count()
        items_by_source[source.value] = count
    
    # Upcoming deadlines (next 7 days)
    upcoming_deadlines = db.query(UnifiedItem).filter(
        and_(
            UnifiedItem.user_id == current_user.id,
            UnifiedItem.deadline.isnot(None),
            UnifiedItem.deadline > datetime.utcnow(),
            UnifiedItem.deadline <= datetime.utcnow() + timedelta(days=7),
            UnifiedItem.status != ItemStatus.COMPLETED
        )
    ).order_by(UnifiedItem.deadline.asc()).limit(10).all()
    
    # Recent updates
    recent_updates = db.query(UnifiedItem).filter(
        UnifiedItem.user_id == current_user.id
    ).order_by(UnifiedItem.updated_at.desc()).limit(10).all()
    
    return DashboardStats(
        total_items=total_items,
        unread_items=unread_items,
        important_items=important_items,
        overdue_items=overdue_items,
        items_by_source=items_by_source,
        upcoming_deadlines=upcoming_deadlines,
        recent_updates=recent_updates
    )


# Reminders
@app.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
    reminder: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a reminder"""
    db_reminder = Reminder(
        user_id=current_user.id,
        item_id=reminder.item_id,
        title=reminder.title,
        description=reminder.description,
        reminder_time=reminder.reminder_time
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@app.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reminders for user"""
    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    ).order_by(Reminder.reminder_time.asc()).all()
    return reminders
