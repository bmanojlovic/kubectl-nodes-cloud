"""Configuration management for kubectl-node-cloud."""

# Default fields shown for all nodes
DEFAULT_FIELDS = [
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

# Provider-specific additional fields
PROVIDER_FIELDS = {
    "aws": [
        "AWS-INSTANCE-ID",
        "AWS-ZONE", 
        "AWS-ASG"
    ],
    "azure": [
        "AZURE-INSTANCE-TYPE"
    ],
    "gcp": [
        "GCP-INSTANCE-ID",
        "GCP-ZONE"
    ],
    "generic": []
}

# Field mappings from Kubernetes node info to display names
FIELD_MAPPINGS = {
    "VERSION": "kubeletVersion",
    "OS-IMAGE": "osImage", 
    "KERNEL-VERSION": "kernelVersion",
    "CONTAINER-RUNTIME": "containerRuntimeVersion"
}

# Cloud provider detection patterns
PROVIDER_DETECTION = {
    "aws": {
        "labels": ["k8s.io/cloud-provider-aws"],
        "annotations": []
    },
    "azure": {
        "labels": ["kubernetes.azure.com/cluster"],
        "annotations": []
    },
    "gcp": {
        "labels": ["cloud.google.com/gke-nodepool"],
        "annotations": []
    }
}
