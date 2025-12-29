#!/usr/bin/env python3
"""
Script to scan for and import all master task lists into the Kanban Scheduler.

This script:
1. Scans your computer for master task list files
2. Shows you what it found
3. Imports them into the kanban scheduler
"""

import requests
import json
import sys
import os

# Configuration
API_BASE = "http://localhost:5000/api"  # Change to your server IP
API_KEY = "your-api-key-here"  # Get this from server/.env (AI_API_KEY)

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def scan_for_task_lists():
    """Scan for master task list files."""
    print("🔍 Scanning for master task lists...")
    
    response = requests.get(
        f"{API_BASE}/import/scan",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['found']} master task list files:\n")
        
        for i, file_info in enumerate(result['files'], 1):
            print(f"{i}. {file_info['name']}")
            print(f"   Path: {file_info['path']}")
            print(f"   Size: {file_info['size']} bytes")
            print(f"   Modified: {file_info['modified']}")
            print()
        
        return result['files']
    else:
        print(f"❌ Error scanning: {response.status_code}")
        print(response.json())
        return []

def import_task_list(user_id, project_id, file_path):
    """Import a single master task list file."""
    print(f"📥 Importing: {file_path}")
    
    payload = {
        "userId": user_id,
        "projectId": project_id,
        "filePath": file_path
    }
    
    response = requests.post(
        f"{API_BASE}/import/import-from-file",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Successfully imported {result['created']} tasks from '{result['template']}'")
        return result
    else:
        print(f"❌ Error importing: {response.status_code}")
        print(response.json())
        return None

def import_all_task_lists(user_id, project_id, file_paths):
    """Import multiple master task list files at once."""
    print(f"📥 Importing {len(file_paths)} master task lists...\n")
    
    payload = {
        "userId": user_id,
        "projectId": project_id,
        "filePaths": file_paths
    }
    
    response = requests.post(
        f"{API_BASE}/import/import-all",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Successfully imported {result['totalCreated']} tasks from {len(result['results'])} files\n")
        
        for file_result in result['results']:
            if file_result['success']:
                print(f"  ✅ {file_result['file']}")
                print(f"     Created {file_result['created']} tasks")
            else:
                print(f"  ❌ {file_result['file']}")
                print(f"     Error: {file_result.get('error', 'Unknown error')}")
            print()
        
        return result
    else:
        print(f"❌ Error importing: {response.status_code}")
        print(response.json())
        return None

if __name__ == "__main__":
    # You need to provide these values
    USER_ID = "your-user-id-here"
    PROJECT_ID = "your-project-id-here"  # Optional, can be None
    
    print("🚀 Master Task List Importer")
    print("=" * 50)
    print()
    
    # Step 1: Scan for files
    found_files = scan_for_task_lists()
    
    if not found_files:
        print("No master task list files found.")
        sys.exit(0)
    
    # Step 2: Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Import all files")
    print("2. Import specific files")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        # Import all
        file_paths = [f['path'] for f in found_files]
        import_all_task_lists(USER_ID, PROJECT_ID, file_paths)
    
    elif choice == "2":
        # Import specific files
        print("\nEnter file numbers to import (comma-separated, e.g., 1,3,5):")
        indices = input().strip().split(',')
        
        selected_files = []
        for idx_str in indices:
            try:
                idx = int(idx_str.strip()) - 1
                if 0 <= idx < len(found_files):
                    selected_files.append(found_files[idx]['path'])
            except ValueError:
                pass
        
        if selected_files:
            import_all_task_lists(USER_ID, PROJECT_ID, selected_files)
        else:
            print("No valid files selected.")
    
    else:
        print("Exiting...")
    
    print("\n💡 To use this script:")
    print("   1. Set USER_ID and PROJECT_ID at the top")
    print("   2. Set API_BASE to your server IP (e.g., http://10.0.0.29:5000/api)")
    print("   3. Set API_KEY from your server/.env file")
    print("   4. Run: python3 import_master_task_lists.py")


