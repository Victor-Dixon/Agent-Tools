# MCP Tools Analysis

**Purpose:** Identify which tools should be MCP-accessible vs unnecessary

**Date:** 2025-12-16

---

## ✅ CRITICAL - Already Created

### 1. Task Manager Server ✅
**Status:** Created  
**Why:** Agents need to update MASTER_TASK_LOG automatically  
**Tools:** add_task_to_inbox, mark_task_complete, move_task_to_waiting, get_tasks

### 2. Website Manager Server ✅
**Status:** Created  
**Why:** Agents need to manage WordPress sites, create content  
**Tools:** WordPress operations, blog automation, image prompts

### 3. Swarm Brain Server ✅
**Status:** Created  
**Why:** Agents need to search knowledge, share learnings, record decisions  
**Tools:** share_learning, record_decision, search_swarm_knowledge, take_note, get_agent_notes

---

## 🔴 HIGH PRIORITY - Should Be MCP

### 4. Git Operations Server
**Why:** Agents need to verify work, check commit status, validate changes  
**Tools:**
- `verify_git_work` - Verify claimed work against git commits
- `get_recent_commits` - Get recent commits for agent
- `check_file_history` - Check file change history
- `validate_commit` - Validate commit before pushing

**Source:** `tools/git_work_verifier.py`, `tools/git_commit_verifier.py`

**Priority:** HIGH - Agents need to verify their work

---

### 5. V2 Compliance Checker Server
**Why:** Agents need to check V2 compliance before committing  
**Tools:**
- `check_v2_compliance` - Check file/function for V2 compliance
- `validate_file_size` - Check file line count
- `check_function_size` - Check function line count
- `get_v2_exceptions` - Get list of approved exceptions

**Source:** `scripts/validate_v2_compliance.py`, `tools/v2_checker_formatters.py`

**Priority:** HIGH - Prevents V2 violations

---

## 🟡 MEDIUM PRIORITY - Consider MCP

### 6. Status Manager Server
**Why:** Agents need to update status.json consistently  
**Tools:**
- `update_agent_status` - Update status.json fields
- `get_agent_status` - Get current agent status
- `update_cycle_count` - Increment cycle count
- `set_fsm_state` - Update FSM state

**Source:** Agent status management code

**Priority:** MEDIUM - Could be useful but status.json updates might be handled differently

---

### 7. Contract System Server
**Why:** Agents need to check contracts, claim tasks  
**Tools:**
- `get_next_contract` - Get next available contract
- `claim_contract` - Claim a contract
- `update_contract_status` - Update contract progress
- `list_available_contracts` - List contracts available to agent

**Source:** Contract system code

**Priority:** MEDIUM - If contract system is actively used

---

## 🟢 LOW PRIORITY - Probably Unnecessary

### 8. File Operations Server
**Why:** Basic file operations are already available via standard tools  
**Tools:** read_file, write_file, list_dir (already available)

**Priority:** LOW - Standard file operations don't need MCP wrapper

---

### 9. Git Basic Operations
**Why:** Basic git operations (commit, push) might be better as CLI  
**Tools:** git_commit, git_push, git_status

**Priority:** LOW - Git operations are complex, CLI might be better

---

### 10. Analysis Tools
**Why:** One-off analysis tools don't need MCP  
**Tools:** Various analysis scripts

**Priority:** LOW - Not frequently used by agents

---

## 📊 Summary

### Should Be MCP (High Priority):
1. ✅ Task Manager - DONE
2. ✅ Website Manager - DONE
3. ✅ Swarm Brain - DONE
4. 🔴 Git Operations - NEEDED
5. 🔴 V2 Compliance Checker - NEEDED

### Consider MCP (Medium Priority):
6. 🟡 Status Manager - Consider
7. 🟡 Contract System - Consider (if actively used)

### Unnecessary (Low Priority):
8. 🟢 File Operations - Already available
9. 🟢 Git Basic Ops - Better as CLI
10. 🟢 Analysis Tools - One-off use

---

## Recommendation

**Create Next:**
1. **Git Operations Server** - Agents need work verification
2. **V2 Compliance Checker Server** - Prevent violations

**Defer:**
- Status Manager (unless agents struggle with status.json)
- Contract System (unless actively used)

**Skip:**
- File operations (already available)
- Basic git ops (CLI is fine)
- Analysis tools (one-off use)

---

## Implementation Order

1. ✅ Task Manager - DONE
2. ✅ Website Manager - DONE
3. ✅ Swarm Brain - DONE
4. 🔴 Git Operations - NEXT
5. 🔴 V2 Compliance - NEXT
6. 🟡 Status Manager - IF NEEDED
7. 🟡 Contract System - IF NEEDED

