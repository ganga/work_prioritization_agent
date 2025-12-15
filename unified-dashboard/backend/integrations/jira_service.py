"""
Jira Integration Service
"""
from jira import JIRA
from typing import List, Dict, Optional
from datetime import datetime


class JiraService:
    def __init__(self, url: str, email: str, api_token: str):
        """Initialize Jira client"""
        self.jira = JIRA(
            server=url,
            basic_auth=(email, api_token)
        )
        self.url = url
    
    def get_my_issues(self, max_results: int = 50) -> List[Dict]:
        """Get issues assigned to the current user"""
        try:
            jql = 'assignee = currentUser() ORDER BY updated DESC'
            issues = self.jira.search_issues(jql, maxResults=max_results)
            
            result = []
            for issue in issues:
                result.append(self._issue_to_dict(issue))
            
            return result
        except Exception as e:
            print(f"Error fetching Jira issues: {e}")
            return []
    
    def get_issues_mentioning_me(self, max_results: int = 50) -> List[Dict]:
        """Get issues where user is mentioned in comments"""
        try:
            # This is a simplified version - in production, you'd search comments
            jql = 'text ~ currentUser() ORDER BY updated DESC'
            issues = self.jira.search_issues(jql, maxResults=max_results)
            
            result = []
            for issue in issues:
                result.append(self._issue_to_dict(issue))
            
            return result
        except Exception as e:
            print(f"Error fetching mentioned issues: {e}")
            return []
    
    def get_high_priority_issues(self, max_results: int = 50) -> List[Dict]:
        """Get high priority issues"""
        try:
            jql = 'priority in (Highest, High) AND assignee = currentUser() ORDER BY updated DESC'
            issues = self.jira.search_issues(jql, maxResults=max_results)
            
            result = []
            for issue in issues:
                result.append(self._issue_to_dict(issue))
            
            return result
        except Exception as e:
            print(f"Error fetching high priority issues: {e}")
            return []
    
    def get_issues_with_deadlines(self, max_results: int = 50) -> List[Dict]:
        """Get issues with due dates"""
        try:
            jql = 'duedate is not EMPTY AND assignee = currentUser() ORDER BY duedate ASC'
            issues = self.jira.search_issues(jql, maxResults=max_results)
            
            result = []
            for issue in issues:
                result.append(self._issue_to_dict(issue))
            
            return result
        except Exception as e:
            print(f"Error fetching issues with deadlines: {e}")
            return []
    
    def _issue_to_dict(self, issue) -> Dict:
        """Convert Jira issue to dictionary"""
        try:
            due_date = None
            if hasattr(issue.fields, 'duedate') and issue.fields.duedate:
                due_date = datetime.combine(issue.fields.duedate, datetime.min.time())
            
            created_date = None
            if hasattr(issue.fields, 'created'):
                created_date = datetime.strptime(issue.fields.created, '%Y-%m-%dT%H:%M:%S.%f%z')
            
            return {
                'id': issue.key,
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': getattr(issue.fields, 'description', ''),
                'status': issue.fields.status.name,
                'priority': getattr(issue.fields, 'priority', {}).name if hasattr(issue.fields, 'priority') and issue.fields.priority else 'Medium',
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else 'Unknown',
                'due_date': due_date,
                'created': created_date or datetime.utcnow(),
                'updated': datetime.strptime(issue.fields.updated, '%Y-%m-%dT%H:%M:%S.%f%z') if hasattr(issue.fields, 'updated') else datetime.utcnow(),
                'url': f"{self.url}/browse/{issue.key}",
                'project': issue.fields.project.key if hasattr(issue.fields, 'project') else 'Unknown'
            }
        except Exception as e:
            print(f"Error converting issue to dict: {e}")
            return {}
    
    def get_issue_details(self, issue_key: str) -> Optional[Dict]:
        """Get detailed information about a specific issue"""
        try:
            issue = self.jira.issue(issue_key)
            return self._issue_to_dict(issue)
        except Exception as e:
            print(f"Error fetching issue details: {e}")
            return None
    
    def calculate_priority_score(self, issue: Dict) -> float:
        """Calculate priority score for an issue"""
        score = 0.0
        
        # Priority level
        priority_map = {
            'Highest': 10,
            'High': 7,
            'Medium': 4,
            'Low': 1,
            'Lowest': 0.5
        }
        score += priority_map.get(issue.get('priority', 'Medium'), 4)
        
        # Due date proximity
        if issue.get('due_date'):
            days_until_due = (issue['due_date'] - datetime.utcnow()).days
            if days_until_due < 0:
                score += 10  # Overdue
            elif days_until_due <= 1:
                score += 8
            elif days_until_due <= 3:
                score += 5
            elif days_until_due <= 7:
                score += 3
        
        # Status (in progress items might be more urgent)
        if issue.get('status') in ['In Progress', 'In Review']:
            score += 2
        
        return min(score, 10.0)  # Cap at 10
