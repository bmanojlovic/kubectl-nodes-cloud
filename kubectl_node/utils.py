"""Utility functions for kubectl-node-cloud."""

import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional

from .exceptions import KubectlCommandError, JSONParseError


def format_timedelta(td):
    """Format timedelta to human readable string."""
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def calculate_node_age(creation_timestamp: str) -> str:
    """Calculate node age from creation timestamp."""
    try:
        creation_time = datetime.strptime(creation_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.utcnow()
        age = format_timedelta(current_time - creation_time)
        return age
    except ValueError as e:
        return "Unknown"


def kubectl_get_nodes(context: Optional[str] = None) -> Dict[str, Any]:
    """Execute kubectl get nodes command and return parsed JSON."""
    command = ["kubectl", "get", "nodes", "-o", "json"]
    
    # Add context if specified
    if context:
        command.extend(["--context", context])
    
    try:
        with subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        ) as process:
            output, error = process.communicate()
            
            if process.returncode != 0:
                # Provide more specific error messages for common issues
                if "context" in error.lower() and context:
                    raise KubectlCommandError(
                        f"Context '{context}' not found. Use 'kubectl config get-contexts' to list available contexts.",
                        stderr=error
                    )
                else:
                    raise KubectlCommandError(
                        f"kubectl command failed with return code {process.returncode}",
                        stderr=error
                    )
            
            return json.loads(output)
            
    except json.JSONDecodeError as e:
        raise JSONParseError(f"Failed to parse kubectl output as JSON: {str(e)}", raw_output=output)
    except Exception as e:
        raise KubectlCommandError(f"Unexpected error executing kubectl: {str(e)}")


def get_current_context() -> str:
    """Get the current kubectl context."""
    try:
        with subprocess.Popen(
            ["kubectl", "config", "current-context"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ) as process:
            output, error = process.communicate()
            
            if process.returncode != 0:
                return "unknown"
            
            return output.strip()
    except Exception:
        return "unknown"


def list_contexts() -> list:
    """List available kubectl contexts."""
    try:
        with subprocess.Popen(
            ["kubectl", "config", "get-contexts", "-o", "name"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        ) as process:
            output, error = process.communicate()
            
            if process.returncode != 0:
                return []
            
            return [ctx.strip() for ctx in output.strip().split('\n') if ctx.strip()]
    except Exception:
        return []


def get_node_status(node: Dict[str, Any]) -> str:
    """Extract and format node status."""
    status = node["status"]
    spec = node["spec"]
    
    # Get the Ready condition
    ready_status = "Unknown"
    for condition in status.get("conditions", []):
        if condition["type"] == "Ready":
            ready_status = "Ready" if condition["status"] == "True" else "NotReady"
            break
    
    # Check if node is unschedulable
    is_unschedulable = spec.get("unschedulable", False)
    if is_unschedulable:
        if ready_status == "Ready":
            return "Ready,SchedulingDisabled"
        else:
            return f"{ready_status},SchedulingDisabled"
    
    return ready_status


def get_node_roles(node: Dict[str, Any]) -> str:
    """Extract node roles from labels."""
    labels = node["metadata"].get("labels", {})
    roles = [
        key.split("/")[1]
        for key in labels.keys()
        if key.startswith("node-role.kubernetes.io/")
    ]
    return ",".join(sorted(roles)) or "<none>"


def get_node_addresses(node: Dict[str, Any]) -> Dict[str, str]:
    """Extract internal and external IP addresses."""
    addresses = node["status"].get("addresses", [])
    
    internal_ip = "N/A"
    external_ip = "N/A"
    
    for addr in addresses:
        if addr["type"] == "InternalIP":
            internal_ip = addr["address"]
        elif addr["type"] == "ExternalIP":
            external_ip = addr["address"]
    
    return {
        "INTERNAL-IP": internal_ip,
        "EXTERNAL-IP": external_ip
    }
