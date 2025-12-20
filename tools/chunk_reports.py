#!/usr/bin/env python3
"""
Report Chunking Utility
========================

Chunks JSON reports into 15k character pieces for agent consumption.
"""

import json
import sys
from pathlib import Path

CHUNK_SIZE = 15000
CHUNK_BUFFER = 100  # Safety buffer to ensure we stay under limit


def chunk_json_report(report_path: Path, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """
    Chunk a JSON report into pieces under chunk_size characters.
    Returns list of JSON strings.
    """
    if not report_path.exists():
        return []

    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    json_str = json.dumps(data, indent=2)

    if len(json_str) <= chunk_size:
        return [json_str]

    chunks = []

    # For dicts, split by top-level keys
    if isinstance(data, dict):
        current_chunk = {}

        for key, value in data.items():
            # Serialize just this key-value pair
            single_item = {key: value}
            item_json = json.dumps(single_item, indent=2)
            item_size = len(item_json)

            # If single item exceeds chunk size, we have a problem
            if item_size > chunk_size:
                # Split the value if it's a list/dict
                if isinstance(value, (list, dict)):
                    # For very large values, we'll include them but note the issue
                    chunks.append(item_json[:chunk_size] + "\n... (truncated)")
                    continue
                else:
                    # For other types, just truncate
                    chunks.append(item_json[:chunk_size])
                    continue

            # Test if adding this key would exceed chunk size
            test_chunk = {**current_chunk, key: value}
            test_json = json.dumps(test_chunk, indent=2)
            test_size = len(test_json)

            # Use buffer to ensure we stay under limit
            effective_limit = chunk_size - 100
            if test_size > effective_limit and current_chunk:
                # Save current chunk (guaranteed to be under size)
                chunk_json = json.dumps(current_chunk, indent=2)
                chunks.append(chunk_json)
                current_chunk = {key: value}
            else:
                current_chunk = test_chunk

        # Save final chunk
        if current_chunk:
            chunk_json = json.dumps(current_chunk, indent=2)
            # Double-check size (should be fine, but verify)
            if len(chunk_json) > chunk_size:
                # Emergency split - shouldn't happen but handle it
                for i in range(0, len(chunk_json), chunk_size):
                    chunks.append(chunk_json[i:i+chunk_size])
            else:
                chunks.append(chunk_json)

    elif isinstance(data, list):
        # For lists, split by items
        current_chunk = []

        for item in data:
            # Serialize just this item
            single_item = [item]
            item_json = json.dumps(single_item, indent=2)
            item_size = len(item_json)

            # If single item exceeds chunk size, truncate it
            if item_size > chunk_size:
                chunks.append(item_json[:chunk_size] + "\n... (truncated)")
                continue

            # Test if adding this item would exceed chunk size
            test_chunk = [*current_chunk, item]
            test_json = json.dumps(test_chunk, indent=2)
            test_size = len(test_json)

            # Use buffer to ensure we stay under limit
            effective_limit = chunk_size - CHUNK_BUFFER
            if test_size > effective_limit and current_chunk:
                # Save current chunk - verify actual size
                chunk_json = json.dumps(current_chunk, indent=2)
                if len(chunk_json) > chunk_size:
                    # Chunk is too large - truncate or split
                    chunks.append(chunk_json[:chunk_size])
                else:
                    chunks.append(chunk_json)
                current_chunk = [item]
            else:
                current_chunk = test_chunk

        # Save final chunk
        if current_chunk:
            chunk_json = json.dumps(current_chunk, indent=2)
            if len(chunk_json) > chunk_size:
                for i in range(0, len(chunk_json), chunk_size):
                    chunks.append(chunk_json[i:i+chunk_size])
            else:
                chunks.append(chunk_json)
    else:
        # Fallback: split string
        chunks = [json_str[i:i+chunk_size]
                  for i in range(0, len(json_str), chunk_size)]

    return chunks


def analyze_report_chunkability(report_path: Path) -> dict:
    """Analyze a report's chunkability."""
    if not report_path.exists():
        return {"error": "File not found"}

    with report_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    json_str = json.dumps(data, indent=2)
    chunks = chunk_json_report(report_path)

    # Verify all chunks are under limit
    oversized_chunks = [i for i, c in enumerate(chunks) if len(c) > CHUNK_SIZE]

    return {
        "file": str(report_path),
        "size_bytes": len(json_str),
        "size_chars": len(json_str),
        "needs_chunking": len(json_str) > CHUNK_SIZE,
        "chunk_count": len(chunks),
        "chunk_sizes": [len(c) for c in chunks],
        "max_chunk_size": max(len(c) for c in chunks) if chunks else 0,
        "min_chunk_size": min(len(c) for c in chunks) if chunks else 0,
        "oversized_chunks": len(oversized_chunks),
        "all_chunks_valid": len(oversized_chunks) == 0,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chunk_reports.py <report_path>")
        sys.exit(1)

    report_path = Path(sys.argv[1])
    analysis = analyze_report_chunkability(report_path)
    print(json.dumps(analysis, indent=2))
