#!/usr/bin/env python3
"""
🐺 Swarm MCP Toolbelt CLI

WE ARE SWARM - A pack of wolves, not bees.
"Alone we are strong. Together we are unstoppable."
"""

import argparse
import sys
from pathlib import Path


def cmd_status(args):
    """Show agent status."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(
        wolves=args.agents.split(",") if args.agents else ["agent-1"],
        den=args.workspace
    )
    
    print("🐺 Swarm Status")
    print("=" * 40)
    
    for agent_id in pack.wolves:
        status = pack.get_status(agent_id)
        if status.role == "alpha":
            icon = "👑"
        elif status.status == "ready":
            icon = "🟢"
        elif status.status == "hunting":
            icon = "🔵"
        else:
            icon = "💤"
        print(f"{icon} {agent_id}: {status.status}")
        if status.current_hunt:
            print(f"   └─ Task: {status.current_hunt[:50]}...")
    
    ready = pack.get_ready_wolves()
    print(f"\n📊 {len(ready)}/{len(pack.wolves)} agents ready")


def cmd_send(args):
    """Send a message."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.messages)
    msg = queue.send(args.sender, args.recipient, args.message)
    
    print(f"✅ Message sent")
    print(f"   From: {msg.sender} → To: {msg.recipient}")
    print(f"   Message: {msg.content[:60]}...")


def cmd_inbox(args):
    """Check inbox for messages."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.messages)
    messages = queue.listen(args.agent, unheard_only=args.unread)
    
    print(f"📬 Inbox for {args.agent}")
    print("=" * 40)
    
    if not messages:
        print("(no messages)")
        return
    
    for msg in messages:
        icon = "📩" if not msg.heard else "✓"
        urgency = "🚨 " if msg.urgency.value <= 2 else ""
        print(f"{icon} {urgency}From {msg.sender}:")
        print(f"   {msg.content[:60]}...")
        print()


def cmd_search(args):
    """Search shared knowledge."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    results = memory.recall(args.query, limit=args.limit)
    
    print(f"🔍 Search results for '{args.query}'")
    print("=" * 40)
    
    if not results:
        print("(nothing found)")
        return
    
    for item in results:
        print(f"📚 {item.title}")
        print(f"   Category: {item.category} | By: {item.wolf_id}")
        print(f"   {item.wisdom[:100]}...")
        print()


def cmd_learn(args):
    """Save something you learned."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    item = memory.share_lore(
        wolf_id=args.agent,
        category=args.category,
        title=args.title,
        wisdom=args.content,
        tags=args.tags.split(",") if args.tags else []
    )
    
    print(f"✅ Knowledge saved!")
    print(f"   Title: {item.title}")
    print(f"   Category: {item.category}")


def cmd_tasks(args):
    """Find tasks in the codebase."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(wolves=["scanner"], den=args.workspace)
    prey = pack.scout_territory(args.path)
    
    print(f"📋 Found {len(prey)} tasks in {args.path}")
    print("=" * 40)
    
    for p in prey[:args.limit]:
        priority = "🔴" if p.difficulty >= 4 else "🟡" if p.difficulty >= 3 else "🟢"
        print(f"{priority} [{p.prey_type.upper()}] {p.description[:50]}...")
        if p.location:
            print(f"   └─ {p.location}")
        print()


def cmd_assign(args):
    """Assign a task to an agent."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(
        wolves=[args.agent],
        den=args.workspace
    )
    
    pack.assign_hunt(args.agent, args.task, difficulty=args.priority)
    
    print(f"✅ Task assigned to {args.agent}")
    print(f"   Task: {args.task[:60]}...")


def cmd_vote(args):
    """Participate in consensus."""
    from .core.consensus import ConsensusEngine, VoteType, ConsensusRule
    
    engine = ConsensusEngine()
    
    if args.create:
        proposal = engine.propose(
            proposer=args.agent,
            title=args.title,
            description=args.description,
            category=args.category,
            rule=ConsensusRule(args.rule)
        )
        print(f"✅ Proposal created: {proposal.id}")
        print(f"   Title: {proposal.title}")
        return

    if args.vote:
        engine.vote(
            proposal_id=args.proposal_id,
            agent_id=args.agent,
            vote=VoteType(args.vote),
            reasoning=args.reasoning
        )
        print(f"🗳️ Vote cast by {args.agent}")
        
        # Check if resolved
        result = engine.resolve(args.proposal_id)
        if result.get("status") == "passed":
            print(f"🎉 Proposal PASSED!")
        elif result.get("status") == "rejected":
            print(f"❌ Proposal REJECTED")
        return

    # List proposals
    proposals = engine.get_open_proposals()
    print(f"🗳️ Open Proposals ({len(proposals)})")
    print("=" * 40)
    
    for p in proposals:
        tally = engine.get_tally(p.id)
        approvals = tally["tally"].get("approve", {}).get("count", 0)
        print(f"📄 {p.title} (ID: {p.id})")
        print(f"   By: {p.proposer} | Rule: {p.rule.value}")
        print(f"   Votes: {approvals} approvals | Status: {p.status}")
        print()


def cmd_conflict(args):
    """Check for conflicts."""
    from .core.conflict import ConflictDetector
    
    detector = ConflictDetector()
    
    if args.check:
        conflicts = detector.check_conflicts(
            agent_id=args.agent,
            files=args.files.split(",") if args.files else [],
            keywords=args.keywords.split(",") if args.keywords else []
        )
        
        if conflicts:
            print(f"⚠️ {len(conflicts)} Conflicts Detected!")
            for c in conflicts:
                print(f"   🔴 {c.severity.value.upper()}: {c.reason}")
                print(f"      Between: {', '.join(c.agents)}")
        else:
            print("✅ No conflicts found. Safe to proceed.")
        return

    # List active intents
    intents = detector.get_active_intents()
    print(f"🚧 Active Work ({len(intents)})")
    print("=" * 40)
    
    for intent in intents:
        print(f"👷 {intent.agent_id}: {intent.description}")
        if intent.files:
            print(f"   Files: {', '.join(intent.files[:3])}...")
        print()


def cmd_profile(args):
    """View agent capabilities."""
    from .core.agent_dna import AgentDNA
    
    dna = AgentDNA()
    
    if args.best:
        result = dna.find_best_agent(category=args.category)
        if result:
            agent, score = result
            print(f"🏆 Best agent for '{args.category}': {agent} (Score: {score:.2f})")
        else:
            print(f"No suitable agent found for '{args.category}'")
        return

    profile = dna.get_profile(args.agent)
    if not profile:
        print(f"No profile found for {args.agent}")
        return
        
    print(f"🧬 Agent DNA: {profile.agent_id}")
    print("=" * 40)
    print(f"Task Count: {profile.total_tasks}")
    print(f"Success Rate: {profile.success_rate:.1%}")
    print(f"Strengths: {', '.join(profile.strengths)}")
    print(f"Weaknesses: {', '.join(profile.weaknesses)}")
    
    if profile.category_scores:
        print("\nTop Categories:")
        for cat, score in sorted(profile.category_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {cat}: {score:.2f}")


def cmd_prove(args):
    """Work proof system."""
    from .core.work_proof import WorkProofSystem
    
    system = WorkProofSystem()
    
    if args.commit:
        commitment = system.commit(
            agent_id=args.agent,
            task=args.task,
            files=args.files.split(",")
        )
        print(f"🔒 Commitment recorded: {commitment.id}")
        return

    if args.generate:
        proof = system.prove(args.id)
        print(f"✅ Proof generated for {proof.agent_id}")
        print(f"   Changes: {len(proof.files_modified)} modified, {len(proof.files_created)} created")
        print(f"   Valid: {proof.valid}")
        return

    if args.verify:
        # Load proof from file (mocking this part as CLI args usually pass ID)
        # In a real CLI we'd read the file content or load by ID
        print("To verify, please inspect the proof file in ./swarm_proofs/proofs/")


def cmd_patterns(args):
    """View mined patterns."""
    from .core.pattern_miner import PatternMiner
    
    miner = PatternMiner()
    
    if args.suggest:
        suggestions = miner.suggest({
            "category": args.category,
            "files": args.files.split(",") if args.files else []
        })
        
        print(f"💡 Suggestions for '{args.category}'")
        print("=" * 40)
        
        if not suggestions:
            print("(no suggestions yet)")
        
        for s in suggestions:
            print(f"✨ {s.pattern_name} ({s.confidence:.0%} confidence)")
            print(f"   {s.reasoning}")
            for action in s.suggested_actions:
                print(f"   👉 {action}")
            print()
        return

    patterns = miner.get_patterns()
    print(f"🧠 Discovered Patterns ({len(patterns)})")
    print("=" * 40)
    
    for p in patterns:
        print(f"🧩 {p.name}")
        print(f"   Type: {p.pattern_type} | Success: {p.success_rate:.0%}")
        print(f"   {p.description}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="🐺 Swarm MCP - Multi-Agent AI Coordination"
    )
    parser.add_argument("--workspace", default="./swarm_workspace", help="Workspace directory")
    parser.add_argument("--messages", default="./swarm_messages", help="Messages directory")
    parser.add_argument("--memory", default="./swarm_memory", help="Shared memory directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status
    status_parser = subparsers.add_parser("status", help="Check which agents are available")
    status_parser.add_argument("--agents", help="Comma-separated agent names")
    status_parser.set_defaults(func=cmd_status)
    
    # send
    send_parser = subparsers.add_parser("send", help="Send a message to an agent")
    send_parser.add_argument("sender", help="Your agent name")
    send_parser.add_argument("recipient", help="Recipient agent name")
    send_parser.add_argument("message", help="Message to send")
    send_parser.set_defaults(func=cmd_send)
    
    # inbox
    inbox_parser = subparsers.add_parser("inbox", help="Check your messages")
    inbox_parser.add_argument("agent", help="Your agent name")
    inbox_parser.add_argument("--unread", action="store_true", help="Only show unread")
    inbox_parser.set_defaults(func=cmd_inbox)
    
    # search
    search_parser = subparsers.add_parser("search", help="Search shared knowledge")
    search_parser.add_argument("query", help="What to search for")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.set_defaults(func=cmd_search)
    
    # learn
    learn_parser = subparsers.add_parser("learn", help="Save something you learned")
    learn_parser.add_argument("--agent", required=True, help="Your agent name")
    learn_parser.add_argument("--category", required=True, help="Category (e.g., debugging, api)")
    learn_parser.add_argument("--title", required=True, help="Short title")
    learn_parser.add_argument("--content", required=True, help="What you learned")
    learn_parser.add_argument("--tags", help="Comma-separated tags")
    learn_parser.set_defaults(func=cmd_learn)
    
    # tasks
    tasks_parser = subparsers.add_parser("tasks", help="Find tasks in the codebase")
    tasks_parser.add_argument("--path", default=".", help="Path to scan")
    tasks_parser.add_argument("--limit", type=int, default=20, help="Max results")
    tasks_parser.set_defaults(func=cmd_tasks)
    
    # assign
    assign_parser = subparsers.add_parser("assign", help="Assign a task to an agent")
    assign_parser.add_argument("agent", help="Agent to assign to")
    assign_parser.add_argument("task", help="Task description")
    assign_parser.add_argument("--priority", type=int, default=3, help="Priority 1-5 (1=highest)")
    assign_parser.set_defaults(func=cmd_assign)

    # vote
    vote_parser = subparsers.add_parser("vote", help="Consensus voting")
    vote_parser.add_argument("--agent", required=True, help="Agent ID")
    vote_parser.add_argument("--create", action="store_true", help="Create new proposal")
    vote_parser.add_argument("--title", help="Proposal title")
    vote_parser.add_argument("--description", help="Proposal description")
    vote_parser.add_argument("--category", default="general", help="Proposal category")
    vote_parser.add_argument("--rule", default="majority", help="Consensus rule")
    vote_parser.add_argument("--vote", help="Vote value (approve/reject)")
    vote_parser.add_argument("--proposal-id", help="Proposal ID to vote on")
    vote_parser.add_argument("--reasoning", help="Reason for vote")
    vote_parser.set_defaults(func=cmd_vote)

    # conflict
    conflict_parser = subparsers.add_parser("conflict", help="Conflict detection")
    conflict_parser.add_argument("--check", action="store_true", help="Check for conflicts")
    conflict_parser.add_argument("--agent", help="Agent ID")
    conflict_parser.add_argument("--files", help="Comma-separated files")
    conflict_parser.add_argument("--keywords", help="Comma-separated keywords")
    conflict_parser.add_argument("--list", action="store_true", help="List active intents")
    conflict_parser.set_defaults(func=cmd_conflict)

    # profile
    profile_parser = subparsers.add_parser("profile", help="Agent capabilities")
    profile_parser.add_argument("--agent", help="Agent ID")
    profile_parser.add_argument("--best", action="store_true", help="Find best agent")
    profile_parser.add_argument("--category", help="Category to find best agent for")
    profile_parser.set_defaults(func=cmd_profile)

    # prove
    prove_parser = subparsers.add_parser("prove", help="Work proof")
    prove_parser.add_argument("--commit", action="store_true", help="Commit to work")
    prove_parser.add_argument("--generate", action="store_true", help="Generate proof")
    prove_parser.add_argument("--verify", action="store_true", help="Verify proof")
    prove_parser.add_argument("--agent", help="Agent ID")
    prove_parser.add_argument("--task", help="Task description")
    prove_parser.add_argument("--files", help="Files involved")
    prove_parser.add_argument("--id", help="Commitment/Proof ID")
    prove_parser.set_defaults(func=cmd_prove)

    # patterns
    patterns_parser = subparsers.add_parser("patterns", help="Pattern mining")
    patterns_parser.add_argument("--suggest", action="store_true", help="Get suggestions")
    patterns_parser.add_argument("--category", help="Context category")
    patterns_parser.add_argument("--files", help="Context files")
    patterns_parser.set_defaults(func=cmd_patterns)
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐺 WE ARE SWARM")
        print("=" * 40)
        print()
        print("Commands:")
        print("  status   - Check which agents are available")
        print("  send     - Send a message to an agent")
        print("  inbox    - Check your messages")
        print("  search   - Search shared knowledge")
        print("  learn    - Save something you learned")
        print("  tasks    - Find tasks in the codebase")
        print("  assign   - Assign a task to an agent")
        print("  vote     - Consensus voting")
        print("  conflict - Conflict detection")
        print("  profile  - Agent capabilities")
        print("  prove    - Work proof system")
        print("  patterns - Pattern mining")
        print()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
