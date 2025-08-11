"""Azure provider implementation."""

from typing import Dict, List, Any
from .base import BaseProvider


class AzureProvider(BaseProvider):
    """Azure cloud provider implementation."""
    
    def __init__(self):
        super().__init__("azure")
    
    def detect(self, node: Dict[str, Any]) -> bool:
        """Detect if node is from Azure."""
        labels = node["metadata"].get("labels", {})
        return "kubernetes.azure.com/cluster" in labels
    
    def get_provider_fields(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Extract Azure-specific fields."""
        labels = node["metadata"].get("labels", {})
        
        # Get instance type
        instance_type = labels.get("node.kubernetes.io/instance-type", "N/A")
        
        # Get resource group
        resource_group = labels.get("kubernetes.azure.com/resource-group", "N/A")
        
        # Get zone
        zone = labels.get("failure-domain.beta.kubernetes.io/zone",
                         labels.get("topology.kubernetes.io/zone", "N/A"))
        
        return {
            "AZURE-INSTANCE-TYPE": instance_type,
            "AZURE-RESOURCE-GROUP": resource_group,
            "AZURE-ZONE": zone
        }
    
    def get_additional_headers(self) -> List[str]:
        """Get Azure-specific headers."""
        return ["AZURE-INSTANCE-TYPE", "AZURE-RESOURCE-GROUP", "AZURE-ZONE"]
