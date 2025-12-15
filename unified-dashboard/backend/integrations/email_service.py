"""
Gmail Integration Service
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
import base64
import re
from typing import List, Dict, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime


class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_json: str):
        """Initialize with credentials JSON string"""
        creds_dict = json.loads(credentials_json)
        self.credentials = Credentials.from_authorized_user_info(creds_dict, self.SCOPES)
        
        # Refresh if needed
        if self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())
        
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_unread_emails(self, max_results: int = 50) -> List[Dict]:
        """Get unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = []
            for msg in results.get('messages', []):
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    messages.append(email_data)
            
            return messages
        except Exception as e:
            print(f"Error fetching unread emails: {e}")
            return []
    
    def get_important_emails(self, max_results: int = 50) -> List[Dict]:
        """Get important emails (starred or with important label)"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:important OR is:starred',
                maxResults=max_results
            ).execute()
            
            messages = []
            for msg in results.get('messages', []):
                email_data = self.get_email_details(msg['id'])
                if email_data:
                    messages.append(email_data)
            
            return messages
        except Exception as e:
            print(f"Error fetching important emails: {e}")
            return []
    
    def get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed email information"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
            
            # Parse date
            date = None
            if date_str:
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    date = datetime.utcnow()
            
            # Get body
            body = self._extract_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'date': date or datetime.utcnow(),
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'thread_id': message.get('threadId'),
                'url': f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
            }
        except Exception as e:
            print(f"Error fetching email details: {e}")
            return None
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html':
                    data = part['body']['data']
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Simple HTML to text conversion
                    body = re.sub('<[^<]+?>', '', html_body)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def extract_deadlines(self, text: str) -> List[datetime]:
        """Extract potential deadlines from email text"""
        # Simple deadline extraction patterns
        patterns = [
            r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        deadlines = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try to parse date
                    date = datetime.strptime(match, '%m/%d/%Y')
                    deadlines.append(date)
                except:
                    try:
                        date = datetime.strptime(match, '%m-%d-%Y')
                        deadlines.append(date)
                    except:
                        pass
        
        return deadlines
    
    def extract_important_keywords(self, text: str) -> List[str]:
        """Extract important keywords from email"""
        important_keywords = [
            "urgent", "asap", "deadline", "important", "critical", "action required",
            "please review", "need your input", "blocking", "priority", "meeting",
            "action items", "follow up"
        ]
        found = []
        text_lower = text.lower()
        for keyword in important_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found
