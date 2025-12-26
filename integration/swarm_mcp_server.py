#!/usr/bin/env python3
"""
Swarm MCP Server
Exposes Swarm functionality (voting, conflicts, DNA, proof, patterns) via MCP.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from swarm_mcp.core.consensus import ConsensusEngine, VoteType, ConsensusRule
from swarm_mcp.core.conflict import ConflictDetector
from swarm_mcp.core.agent_dna import AgentDNA
from swarm_mcp.core.work_proof import WorkProofSystem
from swarm_mcp.core.pattern_miner import PatternMiner

# Initialize engines
consensus_engine = ConsensusEngine()
conflict_detector = ConflictDetector()
agent_dna = AgentDNA()
proof_system = WorkProofSystem()
pattern_miner = PatternMiner()

def swarm_vote(
    agent_id: str,
    proposal_id: Optional[str] = None,
    vote: Optional[str] = None,
    create: bool = False,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: str = "general",
    rule: str = "majority",
    reasoning: str = ""
) -> Dict[str, Any]:
    """Participate in consensus (vote or create proposal)."""
    try:
        if create:
            proposal = consensus_engine.propose(
                proposer=agent_id,
                title=title,
                description=description or title,
                category=category,
                rule=ConsensusRule(rule)
            )
            return {"success": True, "action": "created", "proposal_id": proposal.id}
        
        elif proposal_id and vote:
            consensus_engine.vote(
                proposal_id=proposal_id,
                agent_id=agent_id,
                vote=VoteType(vote),
                reasoning=reasoning
            )
            return {"success": True, "action": "voted"}
        
        else:
            proposals = consensus_engine.get_open_proposals()
            return {
                "success": True,
                "action": "list",
                "proposals": [
                    {"id": p.id, "title": p.title, "proposer": p.proposer}
                    for p in proposals
                ]
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def swarm_check_conflicts(
    agent_id: str,
    files: List[str] = [],
    keywords: List[str] = [],
    check_only: bool = True
) -> Dict[str, Any]:
    """Check for conflicts."""
    try:
        if check_only:
            conflicts = conflict_detector.check_conflicts(
                agent_id=agent_id,
                files=files,
                keywords=keywords
            )
            return {
                "success": True,
                "conflicts": [
                    {
                        "agents": c.agents,
                        "severity": c.severity.value,
                        "reason": c.reason
                    }
                    for c in conflicts
                ]
            }
        else:
            # Declare intent
            intent, conflicts = conflict_detector.declare_intent(
                agent_id=agent_id,
                description=f"Working on {files}",
                files=files,
                keywords=keywords
            )
            return {
                "success": True,
                "action": "declared",
                "conflicts": len(conflicts)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def swarm_get_profile(agent_id: str) -> Dict[str, Any]:
    """Get agent capabilities."""
    try:
        profile = agent_dna.get_profile(agent_id)
        if not profile:
            return {"success": False, "error": "Profile not found"}
        
        return {
            "success": True,
            "profile": {
                "agent_id": profile.agent_id,
                "strengths": profile.strengths,
                "weaknesses": profile.weaknesses,
                "success_rate": profile.success_rate,
                "top_categories": list(profile.category_scores.keys())[:3]
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def swarm_commit_work(agent_id: str, task: str, files: List[str]) -> Dict[str, Any]:
    """Commit to work for proof."""
    try:
        commitment = proof_system.commit(agent_id, task, files)
        return {"success": True, "commitment_id": commitment.id}
    except Exception as e:
        return {"success": False, "error": str(e)}

def swarm_prove_work(commitment_id: str) -> Dict[str, Any]:
    """Generate work proof."""
    try:
        proof = proof_system.prove(commitment_id)
        return {
            "success": True,
            "valid": proof.valid,
            "duration": proof.duration_seconds,
            "files_modified": proof.files_modified
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def swarm_patterns(category: str, files: List[str] = []) -> Dict[str, Any]:
    """Get pattern suggestions."""
    try:
        suggestions = pattern_miner.suggest({"category": category, "files": files})
        return {
            "success": True,
            "suggestions": [
                {
                    "pattern": s.pattern_name,
                    "confidence": s.confidence,
                    "reasoning": s.reasoning,
                    "actions": s.suggested_actions
                }
                for s in suggestions
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """MCP server main loop."""
    print(json.dumps({
        "jsonrpc": "2.0",
        "method": "initialize",
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "swarm_vote": {
                        "description": "Participate in consensus (vote or create proposal)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string"},
                                "create": {"type": "boolean"},
                                "vote": {"type": "string", "enum": ["approve", "reject", "abstain"]},
                                "proposal_id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "category": {"type": "string"},
                                "reasoning": {"type": "string"}
                            },
                            "required": ["agent_id"]
                        }
                    },
                    "swarm_check_conflicts": {
                        "description": "Check for work conflicts",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string"},
                                "files": {"type": "array", "items": {"type": "string"}},
                                "keywords": {"type": "array", "items": {"type": "string"}},
                                "check_only": {"type": "boolean"}
                            },
                            "required": ["agent_id"]
                        }
                    },
                    "swarm_get_profile": {
                        "description": "Get agent capability profile",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string"}
                            },
                            "required": ["agent_id"]
                        }
                    },
                    "swarm_commit_work": {
                        "description": "Commit to work for proof system",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "agent_id": {"type": "string"},
                                "task": {"type": "string"},
                                "files": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["agent_id", "task", "files"]
                        }
                    },
                    "swarm_prove_work": {
                        "description": "Generate proof for committed work",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "commitment_id": {"type": "string"}
                            },
                            "required": ["commitment_id"]
                        }
                    },
                    "swarm_patterns": {
                        "description": "Get pattern suggestions for context",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string"},
                                "files": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["category"]
                        }
                    }
                }
            },
            "serverInfo": {"name": "swarm-toolbelt", "version": "1.0.0"}
        }
    }))
    
    sys.stdout.flush()

    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request.get("method") == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args = params.get("arguments", {})
                
                result = {}
                if name == "swarm_vote":
                    result = swarm_vote(**args)
                elif name == "swarm_check_conflicts":
                    result = swarm_check_conflicts(**args)
                elif name == "swarm_get_profile":
                    result = swarm_get_profile(**args)
                elif name == "swarm_commit_work":
                    result = swarm_commit_work(**args)
                elif name == "swarm_prove_work":
                    result = swarm_prove_work(**args)
                elif name == "swarm_patterns":
                    result = swarm_patterns(**args)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                }))
                sys.stdout.flush()
        except Exception as e:
            # Optionally log error
            pass

if __name__ == "__main__":
    main()
