#!/usr/bin/env python3
"""
Devlog Compression Utility
===========================

Custom compression algorithm optimized for devlog markdown files.
Compresses devlogs for archival storage after Discord posting.

Features:
- Custom markdown-aware compression
- Preserves structure while reducing size
- Fast compression/decompression
- Archive management

Author: Agent-7 (Web Development Specialist)
Date: 2025-01-27
"""

import gzip
import json
import base64
import re
from pathlib import Path
from typing import Optional
from datetime import datetime


class DevlogCompressor:
    """Custom compression for devlog markdown files."""
    
    # Compression settings
    COMPRESSION_LEVEL = 9  # Maximum compression
    ARCHIVE_DIR = Path("devlogs/archive")
    
    def __init__(self, archive_dir: Optional[Path] = None):
        """Initialize compressor with archive directory."""
        self.archive_dir = archive_dir or self.ARCHIVE_DIR
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def preprocess_markdown(self, content: str) -> str:
        """
        Preprocess markdown for better compression.
        - Normalize whitespace
        - Remove redundant blank lines
        - Optimize common patterns
        """
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines (keep max 2 consecutive)
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        # Optimize common markdown patterns
        # Collapse multiple spaces to single space (except in code blocks)
        lines = content.split('\n')
        in_code_block = False
        processed_lines = []
        
        for line in lines:
            # Track code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                processed_lines.append(line)
                continue
            
            if not in_code_block:
                # Collapse multiple spaces outside code blocks
                line = re.sub(r' {2,}', ' ', line)
            
            processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def compress_devlog(
        self, 
        file_path: Path, 
        agent: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Path:
        """
        Compress a devlog file and save to archive.
        
        Returns path to compressed archive file.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Devlog file not found: {file_path}")
        
        # Read and preprocess content
        content = file_path.read_text(encoding='utf-8')
        processed_content = self.preprocess_markdown(content)
        
        # Extract metadata
        if metadata is None:
            metadata = self._extract_metadata(file_path, content, agent)
        
        # Create compressed data structure
        compressed_data = {
            'metadata': metadata,
            'content': processed_content,
            'original_size': len(content),
            'compressed_timestamp': datetime.now().isoformat(),
        }
        
        # Serialize to JSON
        json_data = json.dumps(compressed_data, ensure_ascii=False)
        
        # Compress with gzip
        compressed_bytes = gzip.compress(
            json_data.encode('utf-8'),
            compresslevel=self.COMPRESSION_LEVEL
        )
        
        # Generate archive filename
        archive_filename = self._generate_archive_filename(file_path, agent)
        archive_path = self.archive_dir / archive_filename
        
        # Write compressed file
        archive_path.write_bytes(compressed_bytes)
        
        # Calculate compression ratio
        original_size = len(content.encode('utf-8'))
        compressed_size = len(compressed_bytes)
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"📦 Compressed devlog: {file_path.name}")
        print(f"   Original: {original_size:,} bytes")
        print(f"   Compressed: {compressed_size:,} bytes")
        print(f"   Ratio: {ratio:.1f}% reduction")
        print(f"   Archive: {archive_path}")
        
        return archive_path
    
    def decompress_devlog(self, archive_path: Path) -> dict:
        """
        Decompress a devlog archive file.
        
        Returns dict with 'content' and 'metadata'.
        """
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive file not found: {archive_path}")
        
        # Read compressed file
        compressed_bytes = archive_path.read_bytes()
        
        # Decompress
        try:
            json_data = gzip.decompress(compressed_bytes).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decompress archive: {e}")
        
        # Parse JSON
        compressed_data = json.loads(json_data)
        
        return {
            'content': compressed_data['content'],
            'metadata': compressed_data.get('metadata', {}),
            'original_size': compressed_data.get('original_size', 0),
            'compressed_timestamp': compressed_data.get('compressed_timestamp', ''),
        }
    
    def _extract_metadata(
        self, 
        file_path: Path, 
        content: str, 
        agent: Optional[str] = None
    ) -> dict:
        """Extract metadata from devlog file."""
        metadata = {
            'filename': file_path.name,
            'original_path': str(file_path),
            'agent': agent or self._extract_agent_from_content(content),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Extract date from filename if present
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Extract title from content (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Extract category from content
        if 'repository' in content.lower() or 'repo' in file_path.name.lower():
            metadata['category'] = 'repository_analysis'
        elif 'mission' in content.lower():
            metadata['category'] = 'mission_reports'
        elif 'system' in content.lower() or 'swarm' in content.lower():
            metadata['category'] = 'system_events'
        else:
            metadata['category'] = 'agent_sessions'
        
        return metadata
    
    def _extract_agent_from_content(self, content: str) -> Optional[str]:
        """Extract agent ID from devlog content."""
        # Look for agent mentions
        agent_match = re.search(
            r'(?:Agent|agent)[\s-]?(\d+)',
            content,
            re.IGNORECASE
        )
        if agent_match:
            return f"agent-{agent_match.group(1)}"
        return None
    
    def _generate_archive_filename(
        self, 
        file_path: Path, 
        agent: Optional[str] = None
    ) -> str:
        """Generate archive filename with .devlog.gz extension."""
        # Extract date from filename or use current date
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
        if date_match:
            date_str = date_match.group(1)
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get base filename without extension
        base_name = file_path.stem
        
        # Add agent prefix if available
        if agent:
            agent_prefix = agent.replace('-', '').lower()
            if not base_name.startswith(agent_prefix):
                base_name = f"{agent_prefix}_{base_name}"
        
        # Generate archive filename
        archive_filename = f"{date_str}_{base_name}.devlog.gz"
        
        return archive_filename
    
    def list_archives(self, agent: Optional[str] = None) -> list[Path]:
        """List all archived devlogs, optionally filtered by agent."""
        archives = list(self.archive_dir.glob("*.devlog.gz"))
        
        if agent:
            agent_prefix = agent.replace('-', '').lower()
            archives = [
                a for a in archives 
                if a.name.startswith(agent_prefix) or agent_prefix in a.name
            ]
        
        return sorted(archives, reverse=True)  # Newest first
    
    def get_archive_info(self, archive_path: Path) -> dict:
        """Get information about an archive without decompressing."""
        if not archive_path.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        # Read compressed file
        compressed_bytes = archive_path.read_bytes()
        compressed_size = len(compressed_bytes)
        
        # Decompress just to get metadata (small overhead)
        try:
            data = self.decompress_devlog(archive_path)
            return {
                'filename': archive_path.name,
                'compressed_size': compressed_size,
                'original_size': data.get('original_size', 0),
                'metadata': data.get('metadata', {}),
                'compression_ratio': (
                    (1 - compressed_size / data['original_size']) * 100 
                    if data.get('original_size', 0) > 0 else 0
                ),
            }
        except Exception as e:
            return {
                'filename': archive_path.name,
                'compressed_size': compressed_size,
                'error': str(e),
            }


def compress_and_archive(
    file_path: Path,
    agent: str,
    delete_original: bool = True
) -> Path:
    """
    Convenience function to compress and archive a devlog.
    
    Args:
        file_path: Path to devlog file
        agent: Agent ID
        delete_original: Whether to delete original file after compression
    
    Returns:
        Path to compressed archive file
    """
    compressor = DevlogCompressor()
    archive_path = compressor.compress_devlog(file_path, agent=agent)
    
    if delete_original and file_path.exists():
        file_path.unlink()
        print(f"🗑️  Deleted original file: {file_path}")
    
    return archive_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Devlog Compression Utility"
    )
    
    parser.add_argument(
        'action',
        choices=['compress', 'decompress', 'list', 'info'],
        help='Action to perform'
    )
    
    parser.add_argument(
        '--file', '-f',
        help='File to compress/decompress'
    )
    
    parser.add_argument(
        '--agent', '-a',
        help='Agent ID for metadata'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (for decompress)'
    )
    
    args = parser.parse_args()
    
    compressor = DevlogCompressor()
    
    if args.action == 'compress':
        if not args.file:
            print("❌ --file required for compress action")
            exit(1)
        archive_path = compressor.compress_devlog(
            Path(args.file),
            agent=args.agent
        )
        print(f"✅ Compressed to: {archive_path}")
    
    elif args.action == 'decompress':
        if not args.file:
            print("❌ --file required for decompress action")
            exit(1)
        data = compressor.decompress_devlog(Path(args.file))
        output_path = Path(args.output) if args.output else Path(args.file).with_suffix('.md')
        output_path.write_text(data['content'], encoding='utf-8')
        print(f"✅ Decompressed to: {output_path}")
        print(f"   Metadata: {json.dumps(data['metadata'], indent=2)}")
    
    elif args.action == 'list':
        archives = compressor.list_archives(agent=args.agent)
        print(f"📦 Found {len(archives)} archived devlogs:")
        for archive in archives:
            info = compressor.get_archive_info(archive)
            print(f"   {archive.name} ({info.get('compressed_size', 0):,} bytes)")
    
    elif args.action == 'info':
        if not args.file:
            print("❌ --file required for info action")
            exit(1)
        info = compressor.get_archive_info(Path(args.file))
        print(json.dumps(info, indent=2))

