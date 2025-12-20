#!/usr/bin/env python3
"""
Windows Startup Task Scheduler Setup
====================================

Creates Windows Task Scheduler entry to auto-start queue processor
on system boot.

<!-- SSOT Domain: infrastructure -->

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-08
Priority: HIGH
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
QUEUE_PROCESSOR_SCRIPT = PROJECT_ROOT / "tools" / "start_message_queue_processor.py"
PYTHON_EXE = sys.executable


def create_task_scheduler_entry():
    """Create Windows Task Scheduler entry for queue processor."""
    print("🔧 Setting up Windows Task Scheduler for queue processor...")
    print(f"   Python: {PYTHON_EXE}")
    print(f"   Script: {QUEUE_PROCESSOR_SCRIPT}")
    print()
    
    # Task name
    task_name = "SwarmQueueProcessor"
    
    # Command to run
    command = f'"{PYTHON_EXE}" "{QUEUE_PROCESSOR_SCRIPT}"'
    
    # Working directory
    working_dir = str(PROJECT_ROOT)
    
    # Create task using schtasks command
    create_cmd = [
        "schtasks",
        "/Create",
        "/TN", task_name,
        "/TR", command,
        "/SC", "ONLOGON",  # Start on user logon
        "/RL", "HIGHEST",  # Run with highest privileges
        "/F",  # Force (overwrite if exists)
        "/IT",  # Interactive (allow user interaction if needed)
    ]
    
    # Add working directory (requires /CWD parameter)
    # Note: schtasks doesn't support /CWD directly, so we use PowerShell
    powershell_cmd = [
        "powershell",
        "-Command",
        f"""
        $action = New-ScheduledTaskAction -Execute '{PYTHON_EXE}' -Argument '"{QUEUE_PROCESSOR_SCRIPT}"' -WorkingDirectory '{working_dir}'
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
        """
    ]
    
    try:
        print("📋 Creating Task Scheduler entry...")
        result = subprocess.run(
            powershell_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("✅ Task Scheduler entry created successfully!")
        print(f"   Task Name: {task_name}")
        print(f"   Trigger: On User Logon")
        print(f"   Command: {command}")
        print()
        print("📝 To verify:")
        print(f"   • Open Task Scheduler (taskschd.msc)")
        print(f"   • Look for task: {task_name}")
        print()
        print("📝 To remove:")
        print(f"   schtasks /Delete /TN {task_name} /F")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Task Scheduler entry: {e}")
        print(f"   Error output: {e.stderr}")
        print()
        print("💡 Alternative: Run manually with admin privileges")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    if sys.platform != 'win32':
        print("⚠️  This script is for Windows only.")
        print("   For Linux/Mac, use systemd or launchd instead.")
        return 1
    
    if not QUEUE_PROCESSOR_SCRIPT.exists():
        print(f"❌ Queue processor script not found: {QUEUE_PROCESSOR_SCRIPT}")
        return 1
    
    print("=" * 70)
    print("🚀 WINDOWS STARTUP TASK SCHEDULER SETUP")
    print("=" * 70)
    print()
    
    success = create_task_scheduler_entry()
    
    if success:
        print()
        print("=" * 70)
        print("✅ SETUP COMPLETE")
        print("=" * 70)
        print()
        print("📋 Next Steps:")
        print("   1. Reboot system to test auto-start")
        print("   2. After boot, use !startdiscord in Discord to start bot")
        print("   3. Queue processor will auto-start on logon")
        return 0
    else:
        print()
        print("=" * 70)
        print("❌ SETUP FAILED")
        print("=" * 70)
        print()
        print("💡 Manual Setup:")
        print("   1. Open Task Scheduler (taskschd.msc)")
        print("   2. Create Basic Task")
        print(f"   3. Name: SwarmQueueProcessor")
        print(f"   4. Trigger: When I log on")
        print(f"   5. Action: Start a program")
        print(f"   6. Program: {PYTHON_EXE}")
        print(f"   7. Arguments: \"{QUEUE_PROCESSOR_SCRIPT}\"")
        print(f"   8. Start in: {PROJECT_ROOT}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


