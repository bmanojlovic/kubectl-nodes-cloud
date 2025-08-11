"""Base provider class for cloud provider implementations."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseProvider(ABC):
    """Base class for cloud provider implementations."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def detect(self, node: Dict[str, Any]) -> bool:
        """Detect if this provider matches the given node."""
        pass
    
    @abstractmethod
    def get_provider_fields(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Extract provider-specific fields from node."""
        pass
    
    @abstractmethod
    def get_additional_headers(self) -> List[str]:
        """Get additional headers specific to this provider."""
        pass
    
    def get_provider_id(self, node: Dict[str, Any]) -> str:
        """Extract provider ID from node spec."""
        spec = node.get("spec", {})
        provider_id = spec.get("providerID", "N/A")
        if provider_id != "N/A" and "/" in provider_id:
            return provider_id.split("/")[-1]
        return provider_id
