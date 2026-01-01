# AI Agent API Documentation

This document describes how AI agents can access and update the Kanban Scheduler from remote computers.

## Base URL

The API is accessible at:
- **Local network**: `http://<SERVER_IP>:5000/api/ai`
- **Example**: `http://10.0.0.29:5000/api/ai`

To find the server IP, check the server console output when it starts, or use:
```bash
# On the server machine
hostname -I
```

## Authentication

All AI agent endpoints require an API key in the request header:

```
X-API-Key: <YOUR_API_KEY>
```

The API key is configured in the server's `.env` file as `AI_API_KEY`.

## Available Endpoints

### 1. Get Tasks

Retrieve tasks with optional filtering.

**GET** `/api/ai/tasks`

**Query Parameters:**
- `userId` (optional, UUID): Filter by user ID
- `status` (optional): Filter by status (`TODO`, `IN_PROGRESS`, `IN_REVIEW`, `DONE`, `BLOCKED`, `CANCELLED`)
- `priority` (optional): Filter by priority (`LOW`, `MEDIUM`, `HIGH`, `URGENT`)
- `projectId` (optional, UUID): Filter by project ID
- `limit` (optional, 1-100): Maximum number of tasks to return (default: 50)
- `includeCompleted` (optional, boolean): Include completed tasks (default: false)

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  "http://10.0.0.29:5000/api/ai/tasks?status=TODO&priority=HIGH&limit=10"
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "...",
      "title": "Task title",
      "description": "Task description",
      "status": "TODO",
      "priority": "HIGH",
      "dueDate": "2024-01-01T00:00:00.000Z",
      "aiMetadata": {
        "isOverdue": false,
        "daysUntilDue": 5,
        "completionProgress": null,
        "hasComments": false,
        "lastActivity": "2024-01-01T00:00:00.000Z"
      },
      "project": { ... },
      "user": { ... }
    }
  ],
  "total": 10,
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

### 2. Create Task

Create a new task.

**POST** `/api/ai/tasks`

**Request Body:**
```json
{
  "userId": "user-uuid",
  "title": "Task title",
  "description": "Task description (optional)",
  "status": "TODO",
  "priority": "MEDIUM",
  "dueDate": "2024-01-01T00:00:00.000Z",
  "projectId": "project-uuid (optional)",
  "tags": ["tag1", "tag2"],
  "aiGenerated": true
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-uuid",
    "title": "New task",
    "priority": "HIGH",
    "status": "TODO"
  }' \
  http://10.0.0.29:5000/api/ai/tasks
```

### 3. Update Task

Update an existing task.

**PUT** `/api/ai/tasks/:id`

**Request Body:** (all fields optional)
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "IN_PROGRESS",
  "priority": "URGENT",
  "dueDate": "2024-01-01T00:00:00.000Z",
  "tags": ["updated", "tags"],
  "aiGenerated": true
}
```

**Example:**
```bash
curl -X PUT \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"status": "DONE", "priority": "LOW"}' \
  http://10.0.0.29:5000/api/ai/tasks/task-id
```

### 4. Get Projects

Retrieve projects with insights.

**GET** `/api/ai/projects`

**Query Parameters:**
- `userId` (optional, UUID): Filter by user ID
- `type` (optional): Filter by type (`PERSONAL`, `WORK`, `GITHUB`, `LEARNING`, `HEALTH`, `FINANCE`, `OTHER`)
- `status` (optional): Filter by status (`ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`)
- `limit` (optional, 1-100): Maximum number of projects (default: 50)

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  "http://10.0.0.29:5000/api/ai/projects?status=ACTIVE"
```

**Response includes:**
- Project details
- `aiInsights` with completion percentage, overdue tasks, health score, and recommendations

### 5. Get Dashboard

Get overall dashboard analytics and recommendations.

**GET** `/api/ai/dashboard`

**Query Parameters:**
- `userId` (optional, UUID): Filter by user ID

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  "http://10.0.0.29:5000/api/ai/dashboard?userId=user-uuid"
```

**Response includes:**
- Overview statistics (total tasks, completion rate, overdue tasks, etc.)
- Recent activity
- Global recommendations

## Health Check

Check if the server is running:

**GET** `/health`

**Example:**
```bash
curl http://10.0.0.29:5000/health
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid or missing API key)
- `404` - Not Found
- `500` - Internal Server Error

Error response format:
```json
{
  "error": "Error message",
  "errors": [ /* validation errors if applicable */ ]
}
```

## Python Example

```python
import requests

API_BASE = "http://10.0.0.29:5000/api/ai"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Get tasks
response = requests.get(f"{API_BASE}/tasks", headers=headers, params={
    "status": "TODO",
    "priority": "HIGH"
})
tasks = response.json()

# Create task
new_task = {
    "userId": "user-uuid",
    "title": "New task from agent",
    "priority": "MEDIUM",
    "status": "TODO"
}
response = requests.post(f"{API_BASE}/tasks", headers=headers, json=new_task)
created_task = response.json()

# Update task
update_data = {"status": "IN_PROGRESS"}
response = requests.put(f"{API_BASE}/tasks/{task_id}", headers=headers, json=update_data)
```

## Security Notes

1. **API Key**: Keep your API key secure. Don't commit it to version control.
2. **Network**: The server listens on all interfaces (0.0.0.0) by default. Ensure your firewall is configured appropriately.
3. **HTTPS**: For production use, set up HTTPS/TLS encryption.
4. **Rate Limiting**: The API has rate limiting (1000 requests per 15 minutes per IP).

## Finding Your User ID

To get your user ID for API calls, you can:
1. Log in through the web interface and check the browser's local storage or network requests
2. Query the database directly (if you have access)
3. Use the `/api/auth/me` endpoint with a user JWT token

## Task Templates & Master Task Lists

### 6. Create Tasks from Template

Create multiple tasks from a structured template (perfect for master task lists).

**POST** `/api/templates/create-from-template`

**Request Body:**
```json
{
  "userId": "user-uuid",
  "projectId": "project-uuid (optional)",
  "boardId": "board-uuid (optional)",
  "template": {
    "name": "Master Task List - Project Name",
    "defaultPhase": "0A",
    "categories": [
      {
        "name": "Code Quality",
        "phase": "0A",
        "tasks": [
          {
            "title": "Code review completed",
            "description": "Optional description",
            "priority": "HIGH",
            "tags": ["review", "quality"]
          },
          {
            "title": "Remove console.log statements",
            "priority": "MEDIUM"
          }
        ]
      },
      {
        "name": "Documentation",
        "tasks": [
          {
            "title": "README.md complete with installation instructions"
          }
        ]
      }
    ]
  }
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-uuid",
    "projectId": "project-uuid",
    "template": {
      "name": "Master Task List - Battle Tetris",
      "defaultPhase": "0A",
      "categories": [
        {
          "name": "Code Quality",
          "tasks": [
            {"title": "Code review completed"},
            {"title": "Remove console.log statements"}
          ]
        }
      ]
    }
  }' \
  http://10.0.0.29:5000/api/templates/create-from-template
```

### 7. Create Definition of Done Checklist

Automatically create a Definition of Done checklist for a project.

**POST** `/api/templates/definition-of-done`

**Request Body:**
```json
{
  "userId": "user-uuid",
  "projectId": "project-uuid",
  "categories": ["Code Quality", "Documentation", "Testing", "Security"]
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-uuid",
    "projectId": "project-uuid"
  }' \
  http://10.0.0.29:5000/api/templates/definition-of-done
```

This creates standard Definition of Done tasks for:
- Code Quality
- Documentation
- Testing
- Security
- Performance
- User Experience
- Deployment
- Version Control

### 8. Get Available Templates

Get information about available templates and categories.

**GET** `/api/templates/templates`

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://10.0.0.29:5000/api/templates/templates
```

**Response:**
```json
{
  "definitionOfDone": {
    "name": "Definition of Done",
    "description": "Standard Definition of Done checklist for any project",
    "categories": ["Code Quality", "Documentation", "Testing", ...]
  },
  "phases": {
    "0A": "Organization and Planning",
    "0B": "Research",
    "1": "Design",
    "2": "Development",
    "3": "Testing",
    "4": "Deployment",
    "5": "Maintenance"
  },
  "categories": ["Code Quality", "Documentation", ...]
}
```

## Task Claiming & Management

### 9. Claim a Task

Agents can claim tasks to work on them.

**POST** `/api/ai/tasks/:id/claim`

**Request Body:**
```json
{
  "agentId": "agent-1",
  "agentName": "Agent Name (optional)"
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "agent-1"}' \
  http://10.0.0.29:5000/api/ai/tasks/task-id/claim
```

This will:
- Mark the task as `IN_PROGRESS`
- Record who claimed it
- Prevent other agents from claiming it (unless released)

### 10. Release a Task

Release a claimed task so other agents can work on it.

**POST** `/api/ai/tasks/:id/release`

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  http://10.0.0.29:5000/api/ai/tasks/task-id/release
```

### 11. Get My Claimed Tasks

Get all tasks claimed by a specific agent.

**GET** `/api/ai/tasks/claimed?agentId=agent-1`

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  "http://10.0.0.29:5000/api/ai/tasks/claimed?agentId=agent-1"
```

## Import Master Task Lists

### 12. Scan for Master Task Lists

Scan your computer for master task list files.

**GET** `/api/import/scan`

**Example:**
```bash
curl -H "X-API-Key: your-api-key" \
  http://10.0.0.29:5000/api/import/scan
```

**Response:**
```json
{
  "found": 3,
  "files": [
    {
      "path": "/home/user/Projects/WorkProjects/MASTER_TASK_LIST.md",
      "name": "MASTER_TASK_LIST.md",
      "size": 15234,
      "modified": "2024-12-28T10:30:00.000Z"
    }
  ]
}
```

### 13. Import from File

Import a master task list from a file path.

**POST** `/api/import/import-from-file`

**Request Body:**
```json
{
  "userId": "user-uuid",
  "projectId": "project-uuid (optional)",
  "boardId": "board-uuid (optional)",
  "filePath": "/path/to/MASTER_TASK_LIST.md"
}
```

**Example:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-uuid",
    "projectId": "project-uuid",
    "filePath": "/home/user/Projects/WorkProjects/MASTER_TASK_LIST.md"
  }' \
  http://10.0.0.29:5000/api/import/import-from-file
```

### 14. Import All Files

Import multiple master task list files at once.

**POST** `/api/import/import-all`

**Request Body:**
```json
{
  "userId": "user-uuid",
  "projectId": "project-uuid (optional)",
  "boardId": "board-uuid (optional)",
  "filePaths": [
    "/path/to/file1.md",
    "/path/to/file2.md"
  ]
}
```

## Python Example for Master Task Lists

```python
import requests

API_BASE = "http://10.0.0.29:5000/api"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Create a master task list from your structured template
master_task_list = {
    "userId": "user-uuid",
    "projectId": "project-uuid",
    "template": {
        "name": "Master Task List - Definition of Done",
        "defaultPhase": "0A",
        "categories": [
            {
                "name": "Code Quality",
                "phase": "0A",
                "tasks": [
                    {"title": "Code review completed", "priority": "HIGH"},
                    {"title": "Remove console.log statements"},
                    {"title": "Add JSDoc comments for functions"},
                    {"title": "Consistent code formatting"}
                ]
            },
            {
                "name": "Documentation",
                "phase": "0A",
                "tasks": [
                    {"title": "README.md complete with installation instructions"},
                    {"title": "Usage guide written"},
                    {"title": "Feature list with screenshots"}
                ]
            },
            {
                "name": "Testing",
                "phase": "3",
                "tasks": [
                    {"title": "Unit tests written"},
                    {"title": "Integration tests completed"},
                    {"title": "Manual testing completed"}
                ]
            }
        ]
    }
}

response = requests.post(
    f"{API_BASE}/templates/create-from-template",
    headers=headers,
    json=master_task_list
)

if response.status_code == 201:
    result = response.json()
    print(f"✅ Created {result['created']} tasks!")
    print(f"Template: {master_task_list['template']['name']}")
else:
    print(f"❌ Error: {response.json()}")

# Or create a quick Definition of Done checklist
dod_request = {
    "userId": "user-uuid",
    "projectId": "project-uuid"
}

response = requests.post(
    f"{API_BASE}/templates/definition-of-done",
    headers=headers,
    json=dod_request
)

if response.status_code == 201:
    result = response.json()
    print(f"✅ Created {result['created']} Definition of Done tasks!")
```

