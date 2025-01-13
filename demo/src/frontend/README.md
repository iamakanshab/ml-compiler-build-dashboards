# Build Monitoring System Design Scratchpad(WIP)

## System Overview

The Build Monitoring System provides real-time visibility into build statuses across multiple repositories through three specialized views: Waterfall, Triage, and Developer. The system integrates with GitHub workflows and provides real-time updates through WebSocket connections.

## Architecture

### High-Level Architecture

```
GitHub Webhooks → Flask Backend → SQLite DB ↔ Frontend React App
                         ↓
                    WebSocket
                         ↑ 
                    Real-time
                    Updates
```

## Backend Implementation

### Core Components

1. **Flask Application (`Dashboard` class)**
- Handles webhook events from GitHub
- Manages WebSocket connections
- Provides REST API endpoints
- Interfaces with SQLite database

2. **Database Schema**
```sql
CREATE TABLE repos (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE branches (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    author TEXT,
    repo TEXT NOT NULL
);

CREATE TABLE commits (
    id INTEGER PRIMARY KEY,
    hash TEXT UNIQUE NOT NULL,
    author TEXT,
    message TEXT,
    time REAL NOT NULL,
    repo TEXT NOT NULL
);

CREATE TABLE workflows (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    repo TEXT NOT NULL
);

CREATE TABLE workflowruns (
    id INTEGER PRIMARY KEY,
    branch INTEGER NOT NULL,
    commitid INTEGER NOT NULL,
    workflow INTEGER NOT NULL,
    author TEXT,
    runtime REAL DEFAULT 0.0,
    createtime REAL,
    starttime REAL,
    endtime REAL,
    queuetime REAL DEFAULT 0.0,
    status TEXT,
    conclusion TEXT,
    url TEXT,
    gitid INT UNIQUE,
    archivedbranchname TEXT,
    archivedcommithash TEXT,
    archivedworkflowname TEXT,
    repo TEXT NOT NULL
);
```

### API Endpoints

1. **Webhook Handler**
```python
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    # Handles new branch creation, commits, and workflow runs
```

2. **Build Data Endpoints**
```python
@app.route("/api/builds", methods=["GET"])
def get_builds():
    # Returns paginated build data
    # Supports filtering by branch, repo

@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    # Returns aggregated build metrics
```

3. **WebSocket Connection**
```python
@app.route("/ws")
def websocket_handler():
    # Manages real-time updates
```

### Data Processing Flow

1. **Webhook Processing**
- Receive GitHub webhook
- Parse event type
- Update appropriate database tables
- Broadcast updates via WebSocket

2. **Build Data Management**
- Store build information
- Calculate metrics
- Handle relationship between tables
- Archive historical data

## Frontend Implementation

### Component Structure

1. **Main App Component**
```javascript
BuildMonitorApp
├── Navigation
├── Repository Selector
├── View Selector
└── Content Area
    ├── WaterfallView
    ├── TriageView
    └── DeveloperView
```

### Views Implementation

1. **Waterfall View (HUD-style)**
```javascript
WaterfallView
├── Metrics Grid
│   ├── Success Rate
│   ├── Average Build Time
│   ├── Active Builds
│   └── Failure Rate
├── Performance Chart
└── Build Stream
```

2. **Triage View**
```javascript
TriageView
├── Failed Builds List
└── Build Analysis Grid
```

3. **Developer View**
```javascript
DeveloperView
├── Personal Metrics
└── Personal Build History
```

### Data Management

1. **State Management**
```javascript
const [builds, setBuilds] = useState([]);
const [metrics, setMetrics] = useState({
    successRate: 0,
    avgBuildTime: 0,
    activeBuilds: 0,
    failureRate: 0
});
```

2. **Real-time Updates**
```javascript
useEffect(() => {
    const ws = new WebSocket('ws://localhost:5000/ws');
    ws.onmessage = (event) => {
        const buildData = JSON.parse(event.data);
        setBuilds(prev => [buildData, ...prev].slice(0, 50));
    };
}, []);
```

### Data Flow

1. **Initial Load**
- Fetch initial build data
- Fetch metrics
- Establish WebSocket connection

2. **Real-time Updates**
- Receive WebSocket messages
- Update build list
- Recalculate metrics
- Update visualizations

3. **User Interactions**
- Filter by repository
- Switch between views
- View detailed build information

## Implementation Details

### Backend Performance Optimizations

1. **Database Indexing**
```sql
CREATE INDEX idx_workflowruns_createtime ON workflowruns(createtime);
CREATE INDEX idx_workflowruns_conclusion ON workflowruns(conclusion);
CREATE INDEX idx_branches_name ON branches(name);
```

2. **Query Optimization**
- Use JOIN operations efficiently
- Implement pagination
- Cache frequently accessed data

### Frontend Performance Considerations

1. **Build List Management**
- Keep maximum 50 builds in memory
- Implement virtual scrolling for large lists
- Batch update metrics calculations

2. **Real-time Updates**
- Debounce rapid updates
- Implement reconnection logic
- Buffer WebSocket messages

### Security Considerations

1. **Backend Security**
```python
# Rate limiting
@limiter.limit("100/minute")
def handle_webhook():
    # ...

# Authentication
@require_auth
def get_builds():
    # ...
```

2. **Frontend Security**
- Sanitize WebSocket data
- Validate API responses
- Handle errors gracefully

## Deployment

### Backend Deployment

1. **Environment Configuration**
```python
app.config.update(
    GITHUB_TOKEN=os.getenv('GITHUB_TOKEN'),
    DATABASE_PATH=os.getenv('DATABASE_PATH'),
    WEBSOCKET_PORT=int(os.getenv('WEBSOCKET_PORT', 8765))
)
```

2. **Database Setup**
```bash
python init_db.py -db builds.db -r owner/repo -k github_token -i
```

### Frontend Deployment

1. **Environment Variables**
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:5000/ws';
```

2. **Build Configuration**
- Configure CORS settings
- Set up reverse proxy
- Configure SSL/TLS

## Monitoring and Maintenance

1. **Backend Monitoring**
- Log webhook processing
- Track database performance
- Monitor WebSocket connections

2. **Frontend Monitoring**
- Track component rendering performance
- Monitor WebSocket connection status
- Log error rates

## Future Improvements

1. **Backend Enhancements**
- Implement data archiving
- Add metric aggregation jobs
- Enhance error handling

2. **Frontend Enhancements**
- Add more visualizations
- Implement advanced filtering
- Add customizable dashboards

3. **General Improvements**
- Add user authentication
- Implement role-based access
- Add configuration UI
