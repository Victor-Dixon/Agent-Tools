#!/usr/bin/env python3
"""
Discord Mermaid Renderer
========================

Converts Mermaid diagrams to images for Discord posting.
Discord doesn't support Mermaid natively, so we convert to PNG images.

Author: Agent-4 (Captain)
Date: 2025-01-27
"""

import os
import re
import base64
from pathlib import Path
from typing import List, Tuple, Optional

import requests
from dotenv import load_dotenv
from src.core.config.timeout_constants import TimeoutConstants

load_dotenv()


class DiscordMermaidRenderer:
    """Renders Mermaid diagrams to images for Discord."""

    def __init__(self):
        """Initialize renderer."""
        # Use mermaid.ink API (public service)
        self.mermaid_api = "https://mermaid.ink/img"
        # Alternative: kroki.io
        self.kroki_api = "https://kroki.io/mermaid/png"

    def extract_mermaid_diagrams(self, content: str) -> List[Tuple[str, int]]:
        """
        Extract Mermaid diagrams from markdown content.
        
        Returns:
            List of (diagram_code, start_position) tuples
        """
        diagrams = []
        pattern = r'```mermaid\s*\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            diagram_code = match.group(1).strip()
            start_pos = match.start()
            diagrams.append((diagram_code, start_pos))
        
        return diagrams

    def render_mermaid_to_image_url(self, diagram_code: str) -> Optional[str]:
        """
        Render Mermaid diagram to image URL.
        
        Args:
            diagram_code: Mermaid diagram code
            
        Returns:
            URL to rendered image or None if failed
        """
        try:
            # Encode diagram for URL
            import urllib.parse
            encoded = urllib.parse.quote(diagram_code)
            
            # Use mermaid.ink API
            image_url = f"{self.mermaid_api}/{encoded}"

            # Verify URL works
            response = requests.head(image_url, timeout=TimeoutConstants.HTTP_QUICK)
            if response.status_code == 200:
                return image_url

            # Fallback to kroki.io (base64 payload)
            kroki_diagram = base64.urlsafe_b64encode(
                diagram_code.encode("utf-8")
            ).decode("utf-8").rstrip("=")
            kroki_url = f"{self.kroki_api}/{kroki_diagram}"

            kroki_response = requests.get(kroki_url, timeout=TimeoutConstants.HTTP_SHORT)
            if kroki_response.status_code == 200:
                # kroki returns PNG image directly
                return f"data:image/png;base64,{base64.b64encode(kroki_response.content).decode()}"

            return None
        except Exception as e:
            print(f"⚠️ Failed to render Mermaid: {e}")
            return None

    def render_mermaid_to_file(self, diagram_code: str, output_path: Path) -> bool:
        """
        Render Mermaid diagram to PNG file.
        
        Args:
            diagram_code: Mermaid diagram code
            output_path: Path to save PNG file
            
        Returns:
            True if successful
        """
        try:
            image_url = self.render_mermaid_to_image_url(diagram_code)
            if not image_url:
                return False
            
            # Download image
            if image_url.startswith("data:"):
                # Base64 encoded
                header, encoded = image_url.split(",", 1)
                image_data = base64.b64decode(encoded)
            else:
                # URL
                response = requests.get(image_url, timeout=TimeoutConstants.HTTP_SHORT)
                if response.status_code != 200:
                    return False
                image_data = response.content
            
            # Save to file
            output_path.write_bytes(image_data)
            return True
        except Exception as e:
            print(f"⚠️ Failed to save Mermaid image: {e}")
            return False

    def replace_mermaid_with_images(
        self, content: str, output_dir: Optional[Path] = None
    ) -> Tuple[str, List[Path]]:
        """
        Replace Mermaid diagrams in content with image references.
        
        Args:
            content: Markdown content with Mermaid diagrams
            output_dir: Directory to save images (optional)
            
        Returns:
            (modified_content, list_of_image_paths)
        """
        diagrams = self.extract_mermaid_diagrams(content)
        if not diagrams:
            return content, []
        
        modified_content = content
        image_paths = []
        
        # Process diagrams in reverse order to preserve positions
        for diagram_code, start_pos in reversed(diagrams):
            # Generate image
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                image_filename = f"mermaid_{hash(diagram_code) % 100000}.png"
                image_path = output_dir / image_filename
                
                if self.render_mermaid_to_file(diagram_code, image_path):
                    image_paths.append(image_path)
                    # Replace Mermaid block with image reference
                    pattern = rf'```mermaid\s*\n{re.escape(diagram_code)}```'
                    replacement = f"![Mermaid Diagram]({image_path})"
                    modified_content = re.sub(pattern, replacement, modified_content, flags=re.DOTALL)
            else:
                # Just get URL
                image_url = self.render_mermaid_to_image_url(diagram_code)
                if image_url:
                    pattern = rf'```mermaid\s*\n{re.escape(diagram_code)}```'
                    replacement = f"![Mermaid Diagram]({image_url})"
                    modified_content = re.sub(pattern, replacement, modified_content, flags=re.DOTALL)
        
        return modified_content, image_paths

    def post_to_discord_with_mermaid(
        self,
        content: str,
        webhook_url: str,
        username: str = "Agent-4 (Captain)",
        temp_dir: Optional[Path] = None
    ) -> bool:
        """
        Post content to Discord, converting Mermaid diagrams to images.
        
        Args:
            content: Markdown content
            webhook_url: Discord webhook URL
            username: Discord username
            temp_dir: Temporary directory for images
            
        Returns:
            True if successful
        """
        diagrams = self.extract_mermaid_diagrams(content)
        if not diagrams:
            # No Mermaid diagrams, post as normal
            payload = {"content": content, "username": username}
            response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
            return response.status_code == 204
        
        # Has Mermaid diagrams - convert to images
        temp_dir = temp_dir or Path("temp/discord_images")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        modified_content, image_paths = self.replace_mermaid_with_images(content, temp_dir)
        
        # Post content first
        payload = {"content": modified_content, "username": username}
        response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
        if response.status_code != 204:
            print(f"❌ Failed to post content: {response.status_code}")
            return False
        
        # Post images as separate messages
        for image_path in image_paths:
            try:
                with open(image_path, "rb") as f:
                    files = {"file": (image_path.name, f, "image/png")}
                    data = {"username": username}
                    response = requests.post(
                        webhook_url,
                        files=files,
                        data=data,
                        timeout=TimeoutConstants.HTTP_DEFAULT
                    )
                    if response.status_code == 204:
                        print(f"✅ Posted image: {image_path.name}")
                    else:
                        print(f"⚠️ Failed to post image: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error posting image {image_path}: {e}")
        
        return True


if __name__ == "__main__":
    # Example usage
    renderer = DiscordMermaidRenderer()
    
    # Test content
    test_content = """
    # Test Document
    
    Here's a Mermaid diagram:
    
    ```mermaid
    graph TD
        A[Start] --> B[Process]
        B --> C[End]
    ```
    
    More content here.
    """
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        renderer.post_to_discord_with_mermaid(test_content, webhook_url)
    else:
        print("⚠️ No Discord webhook configured")




