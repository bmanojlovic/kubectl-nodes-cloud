"""Provider manager for automatic cloud provider detection."""

from typing import Dict, List, Any, Optional
from .aws import AWSProvider
from .azure import AzureProvider
from .gcp import GCPProvider
from .generic import GenericProvider
from .base import BaseProvider


class ProviderManager:
    """Manages cloud provider detection and field extraction."""
    
    def __init__(self):
        # Order matters - generic should be last as it always matches
        self.providers = [
            AWSProvider(),
            AzureProvider(), 
            GCPProvider(),
            GenericProvider()  # Fallback
        ]
    
    def detect_provider(self, node: Dict[str, Any]) -> BaseProvider:
        """Detect the cloud provider for a given node."""
        for provider in self.providers:
            if provider.detect(node):
                return provider
        
        # Should never reach here due to GenericProvider fallback
        return GenericProvider()
    
    def get_all_headers(self, nodes: List[Dict[str, Any]]) -> List[str]:
        """Get all headers needed for the given set of nodes."""
        # Base headers that are always shown
        base_headers = [
            "NAME",
            "STATUS", 
            "ROLES",
            "AGE",
            "VERSION",
            "INTERNAL-IP",
            "EXTERNAL-IP",
            "OS-IMAGE",
            "KERNEL-VERSION",
            "CONTAINER-RUNTIME",
            "INSTANCE-TYPE"
        ]
        
        # Collect all provider-specific headers needed
        provider_headers = set()
        for node in nodes:
            provider = self.detect_provider(node)
            provider_headers.update(provider.get_additional_headers())
        
        return base_headers + sorted(list(provider_headers))
    
    def get_node_info(self, node: Dict[str, Any], headers: List[str]) -> List[str]:
        """Extract all information for a node based on required headers."""
        from ..utils import (
            calculate_node_age, 
            get_node_status, 
            get_node_roles, 
            get_node_addresses
        )
        
        metadata = node["metadata"]
        status = node["status"]
        labels = metadata.get("labels", {})
        
        # Base node information
        base_info = {
            "NAME": metadata["name"],
            "STATUS": get_node_status(node),
            "ROLES": get_node_roles(node),
            "AGE": calculate_node_age(metadata["creationTimestamp"]),
            "VERSION": status.get("nodeInfo", {}).get("kubeletVersion", "N/A"),
            "OS-IMAGE": status.get("nodeInfo", {}).get("osImage", "N/A"),
            "KERNEL-VERSION": status.get("nodeInfo", {}).get("kernelVersion", "N/A"),
            "CONTAINER-RUNTIME": status.get("nodeInfo", {}).get("containerRuntimeVersion", "N/A"),
            "INSTANCE-TYPE": labels.get("node.kubernetes.io/instance-type", "N/A"),
            **get_node_addresses(node)
        }
        
        # Get provider-specific information
        provider = self.detect_provider(node)
        provider_info = provider.get_provider_fields(node)
        
        # Combine all information
        all_info = {**base_info, **provider_info}
        
        # Return values in the order of headers
        return [all_info.get(header, "N/A") for header in headers]
