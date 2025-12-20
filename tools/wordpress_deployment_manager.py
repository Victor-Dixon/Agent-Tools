#!/usr/bin/env python3
"""
WordPress Deployment Manager (Backward Compatibility Wrapper)
==============================================================

⚠️  DEPRECATED: This module is maintained for backward compatibility.
    New code should use wordpress_manager.py instead.

This module provides backward compatibility for code using WordPressDeploymentManager.
All functionality has been consolidated into wordpress_manager.py.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
"""

import sys
from pathlib import Path
from typing import Optional

# Import unified manager
sys.path.insert(0, str(Path(__file__).parent))
from wordpress_manager import WordPressManager, ConnectionManager

# Create compatibility wrapper class
class WordPressDeploymentManager(WordPressManager):
    """Backward compatibility wrapper for WordPressManager."""
    
    def deploy_theme_file(self, local_path, remote_subpath="", backup=False):
        """Compatibility method for old deploy_theme_file calls."""
        if isinstance(local_path, str):
            local_path = Path(local_path)
        elif not isinstance(local_path, Path):
            local_path = Path(local_path)
        
        if remote_subpath:
            remote_path = f"{self.config['remote_base']}/{remote_subpath}/{local_path.name}"
        else:
            remote_path = None
        
        return self.deploy_file(local_path, remote_path)
    
    def deploy_plugin_file(self, local_path, plugin_name, remote_subpath="", backup=False):
        """Compatibility method for plugin deployment."""
        if isinstance(local_path, str):
            local_path = Path(local_path)
        elif not isinstance(local_path, Path):
            local_path = Path(local_path)
        
        if remote_subpath:
            remote_path = f"/public_html/wp-content/plugins/{plugin_name}/{remote_subpath}/{local_path.name}"
        else:
            remote_path = f"/public_html/wp-content/plugins/{plugin_name}/{local_path.name}"
        
        return self.deploy_file(local_path, remote_path)
    
    def close(self):
        """Compatibility method for close()."""
        self.disconnect()

# Re-export for backward compatibility
__all__ = ['WordPressDeploymentManager', 'ConnectionManager']
