"""
SDK Registry - Manages SDK configurations from sdks.yaml
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class SDKRegistry:
    """Manages multiple SDK configurations"""
    
    def __init__(self, config_file: str = "sdks.yaml"):
        self.config_file = Path(config_file)
        self.sdks: Dict[str, Dict[str, Any]] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load SDK configurations from YAML file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file {self.config_file} not found")
        
        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)
            self.sdks = config.get('sdks', {})
    
    def get_sdk(self, sdk_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific SDK"""
        return self.sdks.get(sdk_id)
    
    def list_sdks(self) -> List[str]:
        """List all configured SDK IDs"""
        return list(self.sdks.keys())
    
    def get_all_sdks(self) -> Dict[str, Dict[str, Any]]:
        """Get all SDK configurations"""
        return self.sdks
    
    def validate_sdk_config(self, sdk_id: str) -> bool:
        """Validate that SDK configuration has required fields"""
        sdk = self.get_sdk(sdk_id)
        if not sdk:
            return False
        
        required_fields = ['name', 'description', 'source', 'tools']
        source_fields = ['type']
        tool_fields = ['prefix', 'descriptions']
        
        # Check top-level fields
        for field in required_fields:
            if field not in sdk:
                return False
        
        # Check source fields
        source = sdk.get('source', {})
        for field in source_fields:
            if field not in source:
                return False
        
        # Check tool fields
        tools = sdk.get('tools', {})
        for field in tool_fields:
            if field not in tools:
                return False
        
        return True