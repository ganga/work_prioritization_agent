# Unified Dashboard

A comprehensive dashboard application that integrates Slack, Email (Gmail), and Jira into a single unified interface. The application prioritizes important items, tracks deadlines, and provides reminders for critical communications and tasks.

## Features

- **Multi-Platform Integration**: Seamlessly connect Slack, Gmail, and Jira
- **Intelligent Prioritization**: Automatic priority scoring based on keywords, deadlines, sender importance, and user interactions
- **Deadline Tracking**: Track and get reminders for important deadlines
- **Unified View**: See all your important items from different platforms in one place
- **Custom Ranking**: Manually rank items by importance
- **Filtering & Sorting**: Filter by source, status, importance, or overdue items
- **Real-time Updates**: Auto-refresh every 5 minutes or manually sync
- **Reminder System**: Set custom reminders for important items

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy (ORM)
- PostgreSQL/SQLite (Database)
- Slack SDK, Gmail API, Jira API (Integrations)

### Frontend
- React 18
- Vite
- React Router
- Axios
- Date-fns
- Lucide React (Icons)

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (optional, SQLite used by default)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional):
```bash
DATABASE_URL=sqlite:///./unified_dashboard.db
SECRET_KEY=your-secret-key-here
```

5. Run the application:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (optional):
```bash
VITE_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Getting Integration Credentials

### Slack

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app or select an existing one
3. Go to "OAuth & Permissions"
4. Add the following scopes:
   - `channels:read`
   - `groups:read`
   - `im:read`
   - `users:read`
   - `search:read`
5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

### Gmail

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure the OAuth consent screen
6. Create OAuth 2.0 credentials (Web application)
7. Download the credentials JSON
8. Complete the OAuth flow to get a refresh token
9. Paste the credentials JSON in the Settings page

### Jira

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the generated token
4. Use your Jira email and the API token in the Settings page
5. Provide your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)

## Usage

1. **Register/Login**: Create an account or login
2. **Configure Integrations**: Go to Settings and add your credentials for Slack, Gmail, and/or Jira
3. **Sync Data**: Click "Sync Now" on the dashboard to fetch items from all connected platforms
4. **View Items**: All items are displayed with priority scores, deadlines, and source information
5. **Manage Items**: 
   - Mark items as read/unread
   - Star important items
   - Mark items as important
   - Set custom rankings
   - Complete items
6. **Filter & Sort**: Use filters to view specific items (unread, important, overdue) and sort by priority, deadline, or date

## Priority Scoring

Items are automatically scored (0-10) based on:
- **Keywords** (30%): Urgent, ASAP, deadline, important, etc.
- **Deadline Proximity** (40%): How soon the deadline is
- **Sender Importance** (20%): Manager, director, CEO mentions
- **User Interactions** (10%): Starred, marked important, user ranking

## API Endpoints

- `POST /register` - Register a new user
- `POST /token` - Login and get access token
- `GET /me` - Get current user info
- `POST /integrations/slack` - Set Slack credentials
- `POST /integrations/gmail` - Set Gmail credentials
- `POST /integrations/jira` - Set Jira credentials
- `POST /sync` - Sync all integrations
- `GET /items` - Get unified items (with filters)
- `GET /items/{id}` - Get specific item
- `PATCH /items/{id}` - Update item
- `GET /dashboard/stats` - Get dashboard statistics
- `POST /reminders` - Create a reminder
- `GET /reminders` - Get all reminders

## Project Structure

```
unified-dashboard/
├── backend/
│   ├── integrations/
│   │   ├── slack_service.py
│   │   ├── email_service.py
│   │   └── jira_service.py
│   ├── services/
│   │   └── prioritization.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Security Notes

- **Never commit credentials** to version control
- Use environment variables for sensitive data
- In production, encrypt stored credentials
- Use HTTPS for all API communications
- Implement proper token refresh for OAuth flows
- Add rate limiting for API endpoints

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Email notifications for reminders
- [ ] Advanced filtering and search
- [ ] Custom priority rules
- [ ] Team collaboration features
- [ ] Mobile app
- [ ] Analytics and insights
- [ ] Export functionality

## License

MIT License

## Support

For issues or questions, please open an issue on the repository.
