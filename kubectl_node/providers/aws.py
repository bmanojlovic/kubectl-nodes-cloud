"""AWS provider implementation."""

from typing import Dict, List, Any
from .base import BaseProvider


class AWSProvider(BaseProvider):
    """AWS cloud provider implementation."""
    
    def __init__(self):
        super().__init__("aws")
    
    def detect(self, node: Dict[str, Any]) -> bool:
        """Detect if node is from AWS."""
        labels = node["metadata"].get("labels", {})
        return "k8s.io/cloud-provider-aws" in labels
    
    def get_provider_fields(self, node: Dict[str, Any]) -> Dict[str, str]:
        """Extract AWS-specific fields."""
        labels = node["metadata"].get("labels", {})
        spec = node.get("spec", {})
        
        # Get AWS instance ID from provider ID
        instance_id = self.get_provider_id(node)
        
        # Get availability zone
        zone = labels.get("failure-domain.beta.kubernetes.io/zone", 
                         labels.get("topology.kubernetes.io/zone", "N/A"))
        
        # Get ASG information from taints (simplified approach)
        asg_info = ""
        for taint in spec.get("taints", []):
            if taint["key"] != "node.kubernetes.io/unschedulable":
                asg_info = taint.get("key", "")
                break
        
        return {
            "AWS-INSTANCE-ID": instance_id,
            "AWS-ZONE": zone,
            "AWS-ASG": asg_info
        }
    
    def get_additional_headers(self) -> List[str]:
        """Get AWS-specific headers."""
        return ["AWS-INSTANCE-ID", "AWS-ZONE", "AWS-ASG"]
