#!/usr/bin/env python3
"""
Example script for agents to create master task lists in the Kanban Scheduler.

This script demonstrates how to create structured task lists like the ones
shown in the master task list examples.
"""

import requests
import json
import sys

# Configuration
API_BASE = "http://localhost:5000/api"  # Change to your server IP
API_KEY = "your-api-key-here"  # Get this from server/.env (AI_API_KEY)

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def create_master_task_list(user_id, project_id, template_name, categories):
    """
    Create a master task list from a structured template.
    
    Args:
        user_id: UUID of the user
        project_id: UUID of the project (optional, can be None)
        template_name: Name of the master task list
        categories: List of category objects with tasks
    """
    payload = {
        "userId": user_id,
        "projectId": project_id,
        "template": {
            "name": template_name,
            "defaultPhase": "0A",  # Start with Organization & Planning
            "categories": categories
        }
    }
    
    response = requests.post(
        f"{API_BASE}/templates/create-from-template",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Successfully created {result['created']} tasks!")
        print(f"   Template: {template_name}")
        if result.get('errors'):
            print(f"   ⚠️  {len(result['errors'])} errors occurred")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.json()}")
        return None

def create_definition_of_done(user_id, project_id, categories=None):
    """
    Create a standard Definition of Done checklist.
    
    Args:
        user_id: UUID of the user
        project_id: UUID of the project
        categories: Optional list of categories (defaults to all)
    """
    payload = {
        "userId": user_id,
        "projectId": project_id
    }
    
    if categories:
        payload["categories"] = categories
    
    response = requests.post(
        f"{API_BASE}/templates/definition-of-done",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Created Definition of Done with {result['created']} tasks!")
        return result
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.json()}")
        return None

# Example: Create a master task list like the ones in your examples
if __name__ == "__main__":
    # You need to provide these values
    USER_ID = "your-user-id-here"
    PROJECT_ID = "your-project-id-here"  # Optional
    
    # Example: Battle Tetris master task list structure
    battle_tetris_template = [
        {
            "name": "Code Quality",
            "phase": "0A",
            "tasks": [
                {"title": "Code review completed", "priority": "HIGH"},
                {"title": "Remove console.log statements"},
                {"title": "Add JSDoc comments for functions"},
                {"title": "Consistent code formatting (use Prettier/ESLint)"},
                {"title": "Refactor duplicated code"},
                {"title": "Error handling for edge cases (empty inputs, invalid states)"}
            ]
        },
        {
            "name": "Documentation",
            "phase": "0A",
            "tasks": [
                {"title": "README.md complete with installation instructions"},
                {"title": "README.md includes usage guide"},
                {"title": "README.md includes feature list with screenshots/GIFs"},
                {"title": "README.md includes architecture overview"},
                {"title": "Code comments for complex logic"},
                {"title": "Inline documentation for game mechanics"}
            ]
        },
        {
            "name": "Testing",
            "phase": "3",
            "tasks": [
                {"title": "Manual testing: All game modes work correctly"},
                {"title": "Test AI difficulty scaling"},
                {"title": "Test multiplayer functionality (if applicable)"},
                {"title": "Test on multiple browsers (Chrome, Firefox, Safari, Edge)"},
                {"title": "Test responsive design on mobile devices"},
                {"title": "Test edge cases (rapid key presses, window resize, etc.)"},
                {"title": "Performance testing (FPS, memory usage)"}
            ]
        },
        {
            "name": "Security",
            "phase": "0A",
            "tasks": [
                {"title": "Input validation for all user inputs"},
                {"title": "Sanitize any user-generated content"},
                {"title": "No sensitive data in localStorage"},
                {"title": "Content Security Policy headers if deployed"}
            ]
        },
        {
            "name": "Performance",
            "phase": "2",
            "tasks": [
                {"title": "Optimize canvas rendering"},
                {"title": "Reduce memory leaks"},
                {"title": "Optimize game loop (target 60 FPS)"},
                {"title": "Lazy loading if applicable"},
                {"title": "Minimize bundle size"}
            ]
        },
        {
            "name": "User Experience",
            "phase": "2",
            "tasks": [
                {"title": "Polished UI/animations"},
                {"title": "Loading states"},
                {"title": "Helpful error messages"},
                {"title": "Keyboard shortcuts documented"},
                {"title": "Accessibility (keyboard navigation, ARIA labels)"},
                {"title": "Mobile-responsive design"},
                {"title": "Game instructions/tutorial"}
            ]
        },
        {
            "name": "Deployment",
            "phase": "4",
            "tasks": [
                {"title": "Build script (if needed)"},
                {"title": "Deployment documentation"},
                {"title": "Environment variables documented"},
                {"title": "Hosting setup (GitHub Pages, Netlify, etc.)"},
                {"title": "Domain configuration (if applicable)"}
            ]
        }
    ]
    
    print("🚀 Creating Master Task List for Battle Tetris...")
    print(f"   User ID: {USER_ID}")
    print(f"   Project ID: {PROJECT_ID or 'None (will create in default board)'}")
    print()
    
    # Uncomment to create the task list:
    # result = create_master_task_list(
    #     USER_ID,
    #     PROJECT_ID,
    #     "Master Task List - Battle Tetris",
    #     battle_tetris_template
    # )
    
    # Or create a quick Definition of Done:
    # result = create_definition_of_done(USER_ID, PROJECT_ID)
    
    print("\n💡 To use this script:")
    print("   1. Set USER_ID and PROJECT_ID at the top")
    print("   2. Set API_BASE to your server IP (e.g., http://10.0.0.29:5000/api)")
    print("   3. Set API_KEY from your server/.env file")
    print("   4. Uncomment the create_master_task_list() call")
    print("   5. Run: python3 create_master_task_list.py")


