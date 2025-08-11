"""Generic provider for non-cloud or unknown providers."""

from typing import Dict, List, Any
from .base import BaseProvider


class GenericProvider(BaseProvider):
    """Generic provider for non-cloud clusters."""
    
    def __init__(self):
        super().__init__("generic")
    
    def detect(self, node: Dict[str, Any]) -> bool:
        """Generic provider always matches as fallback."""
        return True
    
    def get_provider_fields(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Generic provider has no additional fields."""
        return {}
    
    def get_additional_headers(self) -> List[str]:
        """Generic provider has no additional headers."""
        return []
