# 🚀 Agent Quick Start Guide

## Super Simple: Create Master Task Lists

Your agents can now easily create structured master task lists like the ones you showed me!

### Option 1: Quick Definition of Done (Easiest!)

```python
import requests

API_BASE = "http://YOUR_IP:5000/api"
API_KEY = "your-api-key"  # From server/.env

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Create Definition of Done checklist
response = requests.post(
    f"{API_BASE}/templates/definition-of-done",
    headers=headers,
    json={
        "userId": "user-uuid",
        "projectId": "project-uuid"
    }
)

print(f"✅ Created {response.json()['created']} tasks!")
```

This automatically creates tasks for:
- ✅ Code Quality
- ✅ Documentation  
- ✅ Testing
- ✅ Security
- ✅ Performance
- ✅ User Experience
- ✅ Deployment
- ✅ Version Control

### Option 2: Custom Master Task List

```python
import requests

API_BASE = "http://YOUR_IP:5000/api"
API_KEY = "your-api-key"

headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Create your structured task list
master_list = {
    "userId": "user-uuid",
    "projectId": "project-uuid",
    "template": {
        "name": "Master Task List - My Project",
        "defaultPhase": "0A",  # Organization & Planning
        "categories": [
            {
                "name": "Code Quality",
                "phase": "0A",
                "tasks": [
                    {"title": "Code review completed", "priority": "HIGH"},
                    {"title": "Remove console.log statements"},
                    {"title": "Add code comments"}
                ]
            },
            {
                "name": "Documentation",
                "phase": "0A",
                "tasks": [
                    {"title": "README.md complete"},
                    {"title": "Usage guide written"}
                ]
            },
            {
                "name": "Testing",
                "phase": "3",
                "tasks": [
                    {"title": "Unit tests written"},
                    {"title": "Integration tests completed"}
                ]
            }
        ]
    }
}

response = requests.post(
    f"{API_BASE}/templates/create-from-template",
    headers=headers,
    json=master_list
)

print(f"✅ Created {response.json()['created']} tasks!")
```

## Available Categories

Use these standard categories (or create your own):

- `Code Quality`
- `Documentation`
- `Testing`
- `Security`
- `Performance`
- `User Experience`
- `Deployment`
- `Version Control`

## Available Phases

- `0A` - Organization and Planning (START HERE!)
- `0B` - Research
- `1` - Design
- `2` - Development
- `3` - Testing
- `4` - Deployment
- `5` - Maintenance

## Task Priorities

- `LOW`
- `MEDIUM` (default)
- `HIGH`
- `URGENT`

## Example: Full Master Task List

```python
# Example matching your master task list structure
template = {
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
                {"title": "Consistent code formatting"},
                {"title": "Refactor duplicated code"},
                {"title": "Error handling for edge cases"}
            ]
        },
        {
            "name": "Documentation",
            "phase": "0A",
            "tasks": [
                {"title": "README.md complete with installation instructions"},
                {"title": "README.md includes usage guide"},
                {"title": "README.md includes feature list with screenshots"},
                {"title": "Code comments for complex logic"}
            ]
        },
        {
            "name": "Testing",
            "phase": "3",
            "tasks": [
                {"title": "Unit tests written"},
                {"title": "Integration tests completed"},
                {"title": "Manual testing completed"},
                {"title": "Test edge cases"},
                {"title": "Cross-platform testing"}
            ]
        },
        {
            "name": "Security",
            "phase": "0A",
            "tasks": [
                {"title": "Input validation on all user inputs"},
                {"title": "Security vulnerabilities fixed"},
                {"title": "No sensitive data exposed"},
                {"title": "Proper error handling"}
            ]
        },
        {
            "name": "Performance",
            "phase": "2",
            "tasks": [
                {"title": "Performance optimization completed"},
                {"title": "Load testing (if applicable)"},
                {"title": "Memory leaks fixed"}
            ]
        },
        {
            "name": "User Experience",
            "phase": "2",
            "tasks": [
                {"title": "Polished UI/animations"},
                {"title": "Helpful error messages"},
                {"title": "Loading states implemented"},
                {"title": "Accessibility improvements"}
            ]
        },
        {
            "name": "Deployment",
            "phase": "4",
            "tasks": [
                {"title": "Build process works"},
                {"title": "Deployment documentation"},
                {"title": "Environment variables documented"},
                {"title": "Hosting setup complete"}
            ]
        }
    ]
}
```

## Getting Your IDs

1. **User ID**: Log into the web app, check browser DevTools → Network → look for API calls
2. **Project ID**: Create a project in the web app, or use the API to list projects
3. **API Key**: Check `server/.env` file for `AI_API_KEY`

## Quick Test

```bash
# Test the API is working
curl -H "X-API-Key: your-api-key" \
  http://YOUR_IP:5000/api/templates/templates

# Should return available templates and phases
```

## Task Claiming & Updates

### Claim a Task
```python
# Claim a task to work on it
response = requests.post(
    f"{API_BASE}/ai/tasks/{task_id}/claim",
    headers=headers,
    json={"agentId": "agent-1"}
)
```

### Update Task Status
```python
# Mark task as complete
response = requests.put(
    f"{API_BASE}/ai/tasks/{task_id}",
    headers=headers,
    json={
        "status": "DONE",
        "agentId": "agent-1"
    }
)
```

### Get My Claimed Tasks
```python
# See what tasks you're working on
response = requests.get(
    f"{API_BASE}/ai/tasks/claimed?agentId=agent-1",
    headers=headers
)
claimed_tasks = response.json()['tasks']
```

## Import Existing Master Task Lists

### Scan for Files
```python
# Find all master task lists on your computer
response = requests.get(
    f"{API_BASE}/import/scan",
    headers=headers
)
found_files = response.json()['files']
```

### Import a File
```python
# Import a master task list
response = requests.post(
    f"{API_BASE}/import/import-from-file",
    headers=headers,
    json={
        "userId": "user-uuid",
        "projectId": "project-uuid",
        "filePath": "/path/to/MASTER_TASK_LIST.md"
    }
)
```

## That's It!

Your agents can now:
1. ✅ Create structured master task lists
2. ✅ Organize by categories (Code Quality, Documentation, etc.)
3. ✅ Assign phases (0A, 0B, 1, 2, 3, 4, 5)
4. ✅ Set priorities
5. ✅ Link to projects
6. ✅ Track Definition of Done criteria
7. ✅ **Claim tasks** to work on them
8. ✅ **Update task status** as they work
9. ✅ **Import existing master task lists** from your computer
10. ✅ **See what tasks they're working on**

All tasks are automatically created and organized in your kanban board! 🎉

