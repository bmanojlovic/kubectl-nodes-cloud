import json
import subprocess
from tabulate import tabulate
from datetime import datetime
import sys
import os


def detect_cloud_provider(node):
    labels = node["metadata"].get("labels", {})
    annotations = node["metadata"].get("annotations", {})

    if "k8s.io/cloud-provider-aws" in labels:
        return "aws"
    elif "kubernetes.azure.com/cluster" in labels:
        return "azure"
    elif "cloud.google.com/gke-nodepool" in labels:
        return "gcp"
    else:
        return "generic"


def format_timedelta(td):
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


def kubectl_get_nodes():
    # command = "cat /Users/steki/nodovi.json"
    command = "kubectl get nodes -o json"
    try:
        with subprocess.Popen(
            command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as process:
            output, error = process.communicate()
            if process.returncode != 0:
                print(f"Error executing command: {error}")
                sys.exit(1)
            return json.loads(output)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {str(e)}")
        print("Raw output:")
        print(output)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


def get_node_info(node):
    metadata = node["metadata"]
    status = node["status"]
    spec = node["spec"]
    labels = metadata["labels"]
    provider = detect_cloud_provider(node)

    creation_timestamp = datetime.strptime(
        metadata["creationTimestamp"], "%Y-%m-%dT%H:%M:%SZ"
    )
    current_time = datetime.utcnow()
    age = format_timedelta(current_time - creation_timestamp)

    # Get the Ready condition
    ready_status = next(
        (
            condition["type"] if condition["status"] == "True" else "NotReady"
            for condition in status["conditions"]
            if condition["type"] == "Ready"
        ),
        "Unknown",
    )

    # Check if node is unschedulable and update status accordingly
    is_unschedulable = spec.get("unschedulable", False)
    if is_unschedulable:
        if ready_status == "Ready":
            node_status = "Ready,SchedulingDisabled"
        else:
            node_status = f"{ready_status},SchedulingDisabled"
    else:
        node_status = ready_status

    node_info = {
        "NAME": metadata["name"],
        "STATUS": node_status,
        "ROLES": ",".join(
            sorted(
                [
                    key.split("/")[1]
                    for key in labels.keys()
                    if key.startswith("node-role.kubernetes.io/")
                ]
            )
        )
        or "<none>",
        "AGE": str(age),
        **{
            k: status.get("nodeInfo", {}).get(v, "N/A")
            for k, v in {
                "VERSION": "kubeletVersion",
                "OS-IMAGE": "osImage",
                "KERNEL-VERSION": "kernelVersion",
                "CONTAINER-RUNTIME": "containerRuntimeVersion",
            }.items()
        },
        "INTERNAL-IP": next(
            (
                addr["address"]
                for addr in status.get("addresses", [])
                if addr["type"] == "InternalIP"
            ),
            "N/A",
        ),
        "EXTERNAL-IP": next(
            (
                addr["address"]
                for addr in status.get("addresses", [])
                if addr["type"] == "ExternalIP"
            ),
            "N/A",
        ),
        "INSTANCE-TYPE": labels.get("node.kubernetes.io/instance-type", "N/A"),
        "PROVIDER": provider,
    }

    if provider == "aws":
        node_info["AWS-INSTANCE-ID"] = (
            spec.get("providerID", "N/A").split("/")[-1]
            if spec.get("providerID")
            else "N/A"
        )
        node_info["AWS-ZONE"] = labels.get(
            "failure-domain.beta.kubernetes.io/zone", "N/A"
        )
        node_info["AWS-ASG"] = next(
            (
                taint["key"]
                for taint in spec.get("taints", [])
                if taint["key"] != "node.kubernetes.io/unschedulable"
            ),
            "",
        )
    elif provider == "azure":
        node_info["AZURE-INSTANCE-TYPE"] = node_info["INSTANCE-TYPE"]
    elif provider == "gcp":
        node_info["GCP-INSTANCE-ID"] = (
            spec.get("providerID", "N/A").split("/")[-1]
            if spec.get("providerID")
            else "N/A"
        )
        node_info["GCP-ZONE"] = labels.get(
            "failure-domain.beta.kubernetes.io/zone", "N/A"
        )

    return node_info


def display_nodes():
    nodes_data = kubectl_get_nodes()
    headers = {
        "aws": [
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
            "AWS-INSTANCE-ID",
            "AWS-ZONE",
            "INSTANCE-TYPE",
            "AWS-ASG",
        ],
        "azure": [
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
            "AZURE-INSTANCE-TYPE",
        ],
        "gcp": [
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
            "GCP-INSTANCE-ID",
            "GCP-ZONE",
            "INSTANCE-TYPE",
        ],
        "generic": [
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
            "INSTANCE-TYPE",
        ],
    }

    data = []
    for node in nodes_data["items"]:
        node_info = get_node_info(node)
        provider = node_info["PROVIDER"]
        selected_headers = headers.get(provider, headers["generic"])
        data.append([node_info.get(h, "N/A") for h in selected_headers])

    print(tabulate(data, headers=selected_headers, tablefmt="plain"))


def main():
    display_nodes()


if __name__ == "__main__":
    main()
