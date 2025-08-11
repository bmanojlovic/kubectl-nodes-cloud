"""GCP provider implementation."""

from typing import Dict, List, Any
from .base import BaseProvider


class GCPProvider(BaseProvider):
    """GCP cloud provider implementation."""
    
    def __init__(self):
        super().__init__("gcp")
    
    def detect(self, node: Dict[str, Any]) -> bool:
        """Detect if node is from GCP."""
        labels = node["metadata"].get("labels", {})
        return "cloud.google.com/gke-nodepool" in labels
    
    def get_provider_fields(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Extract GCP-specific fields."""
        labels = node["metadata"].get("labels", {})
        
        # Get instance ID from provider ID
        instance_id = self.get_provider_id(node)
        
        # Get zone
        zone = labels.get("failure-domain.beta.kubernetes.io/zone",
                         labels.get("topology.kubernetes.io/zone", "N/A"))
        
        # Get node pool
        node_pool = labels.get("cloud.google.com/gke-nodepool", "N/A")
        
        # Get preemptible status
        preemptible = labels.get("cloud.google.com/gke-preemptible", "false")
        
        return {
            "GCP-INSTANCE-ID": instance_id,
            "GCP-ZONE": zone,
            "GCP-NODE-POOL": node_pool,
            "GCP-PREEMPTIBLE": preemptible
        }
    
    def get_additional_headers(self) -> List[str]:
        """Get GCP-specific headers."""
        return ["GCP-INSTANCE-ID", "GCP-ZONE", "GCP-NODE-POOL", "GCP-PREEMPTIBLE"]
