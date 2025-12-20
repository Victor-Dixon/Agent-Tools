#!/usr/bin/env python3
"""Post Agent-2 session cleanup devlog to Discord."""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    webhook_url = os.getenv('DISCORD_WEBHOOK_AGENT_2')
    if not webhook_url:
        print('❌ No DISCORD_WEBHOOK_AGENT_2 env set; cannot post devlog')
        return False

    content = """# Agent-2 Session Cleanup – 2025-12-10

**Agent**: Agent-2 (Architecture & Design Specialist)  
**Date**: 2025-12-10  
**Type**: Session Cleanup + FreeRideInvestor Theme Redesign  
**Status**: ✅ **HOMEPAGE REDESIGN COMPLETE - DEPLOYMENT PENDING**

---

## 🎯 **SESSION SUMMARY**

**FreeRideInvestor V2 theme completely redesigned as personal trading journal!**

### **Major Accomplishments** ✅

1. **Homepage Redesign** (100% Complete):
   - ✅ Rebuilt `home.php` as personal trading journal layout
   - ✅ Added "Today's Plan" block (top priority section)
   - ✅ Split content: "Latest Journal Entries" vs "Deep Dives & Articles"
   - ✅ Added Performance/Process snapshot section
   - ✅ Added Rules/Risk Framework section
   - ✅ Updated hero copy to personal voice
   - ✅ Updated CTAs to journal-specific actions

2. **Styling Updates** (100% Complete):
   - ✅ Updated `style.css` with dark trading aesthetic
   - ✅ Styled all new journal sections
   - ✅ Responsive mobile layout
   - ✅ Trading green (#00d4aa) accent colors
   - ✅ Dashboard-style cards with gradients

3. **Deployment Preparation** (Ready):
   - ✅ Created `tools/deploy_freeride_corrected.py` deployment script
   - ⚠️ **BLOCKER**: Missing `pysftp` dependency on host

---

## 🚨 **DEPLOYMENT BLOCKER**

**Issue**: `pysftp` module not installed  
**Solution**: Run `pip install pysftp` then execute deployment script

**Deployment Command**:
```bash
pip install pysftp
python tools/deploy_freeride_corrected.py
```

**Files Ready for Deployment**:
- `D:/websites/FreeRideInvestor_V2/home.php` (redesigned)
- `D:/websites/FreeRideInvestor_V2/style.css` (updated)
- `D:/websites/FreeRideInvestor_V2/functions.php`
- `D:/websites/FreeRideInvestor_V2/index.php`
- `D:/websites/FreeRideInvestor_V2/header.php`
- `D:/websites/FreeRideInvestor_V2/footer.php`
- `D:/websites/FreeRideInvestor_V2/sidebar.php`
- `D:/websites/FreeRideInvestor_V2/js/theme.js`

---

## 🎨 **THEME REDESIGN HIGHLIGHTS**

### **Personal Trading Journal Identity**:
- ✅ **Today's Plan Block**: Date, market bias, watchlist, daily rules, if/then scenarios
- ✅ **Performance Snapshot**: Week's focus, compliance streak, risk cap
- ✅ **Journal Entries**: Daily plans and trade recaps (separate from articles)
- ✅ **Rules Framework**: Position sizing, entry/exit rules, discipline rules
- ✅ **Personal Voice**: "A real-time trading journal — daily plans, recap notes, rules, and lessons"

### **Design Features**:
- ✅ Dark trading aesthetic (navy #1a1a2e background)
- ✅ Trading green (#00d4aa) accent colors
- ✅ Dashboard-style cards with gradients
- ✅ Technical typography (SF Mono for data)
- ✅ Responsive mobile layout

---

## 📋 **NEXT SESSION PRIORITIES**

### **Immediate**:
1. Install `pysftp` dependency
2. Deploy corrected theme via SFTP
3. Verify live site displays journal layout correctly
4. Flush WordPress cache if needed

### **Follow-up**:
1. Monitor site performance after deployment
2. Gather user feedback on journal layout
3. Iterate on Today's Plan content structure if needed

---

## 🛠️ **TOOLS CREATED**

- ✅ `tools/deploy_freeride_corrected.py` - SFTP deployment script
- ✅ `tools/WISHLIST_WP_SFTP_CHECKER.md` - Wishlist tool documentation

---

## 📊 **FILES UPDATED**

- ✅ `agent_workspaces/Agent-2/passdown.json` - Session handoff
- ✅ `devlogs/2025-12-10_agent-2_session_cleanup.md` - Final devlog
- ✅ `D:/websites/FreeRideInvestor_V2/home.php` - Redesigned homepage
- ✅ `D:/websites/FreeRideInvestor_V2/style.css` - Updated styling

---

**Status**: ✅ **HOMEPAGE REDESIGN COMPLETE - DEPLOYMENT PENDING**

🐝 WE. ARE. SWARM. ⚡🔥"""

    # Prepare Discord embed
    embed = {
        'title': 'Agent-2 Session Cleanup – FreeRideInvestor Theme Redesign Complete',
        'description': content[:2000],  # Discord embed limit
        'color': 0x00d4aa,  # Trading green
        'footer': {'text': 'Architecture & Design Specialist - Agent-2'},
        'timestamp': '2025-12-10T05:10:00.000Z'
    }

    payload = {
        'embeds': [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print('✅ Session cleanup devlog posted to Discord!')
            return True
        else:
            print(f'❌ Failed to post: {response.status_code}')
            print(f'Response: {response.text}')
            return False
    except Exception as e:
        print(f'❌ Error posting devlog: {e}')
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)





