import json
import subprocess
from tabulate import tabulate
from datetime import datetime
import sys
import os

def format_timedelta(td):
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    if days > 0:
        return f"{days}d"
    elif hours > 0:
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def kubectl_get_nodes():
    command = "kubectl get nodes -o json"
    #command = "cat get_nodes.json"
    #command = "cat nodes_all.json"
    #command = "cat nodes_notready.json"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return json.loads(output)


def get_node_info(node, provider):
    metadata = node['metadata']
    status = node['status']
    spec = node['spec']
    taints = spec.get('taints',{})

    creation_timestamp = datetime.strptime(metadata['creationTimestamp'], "%Y-%m-%dT%H:%M:%SZ")
    current_time = datetime.utcnow()
    age = format_timedelta(current_time - creation_timestamp)

    node_info = {
        'name': metadata['name'],
        'instance_type': metadata['labels'].get('node.kubernetes.io/instance-type', 'N/A'),
        'status': next((condition['status'] for condition in status['conditions'] if condition['type'] == 'Ready'), 'N/A'),
        'age': str(age),
        'os': metadata['labels'].get('kubernetes.io/os', 'N/A'),
        'version': status.get('nodeInfo', {}).get('kubeletVersion', 'N/A'),
        'internal_ip': next((addr['address'] for addr in status.get('addresses', []) if addr['type'] == 'InternalIP'), 'N/A'),
        'external_ip': next((addr['address'] for addr in status.get('addresses', []) if addr['type'] == 'ExternalIP'), 'N/A'),
    }

    if provider == 'aws':
        node_info['aws_instance_id'] = spec.get('providerID', 'N/A').split('/')[-1] if spec.get('providerID') else 'N/A'
        node_info['aws_zone'] = metadata['labels'].get('failure-domain.beta.kubernetes.io/zone', 'N/A')
        node_info['aws_asg'] = taints[0].get('key','N/A') if len(taints) > 0 and taints[0].get('key','N/A') != 'node.kubernetes.io/unschedulable' else ''

    return node_info

def aws():
    nodes_data = kubectl_get_nodes()
    data = []
    for node in nodes_data['items']:
        node_info = get_node_info(node, 'aws')
        data.append(node_info)
    headers = {'name':'name',
               'aws_instance_id':'aws_instance_id',
               'aws_zone':'aws_zone',
               'aws_instance_type':'aws_instance_type',
               'status':'status',
               'age':'age',
               'os': 'os',
               'version':'version',
               'internal_ip':'internal_ip',
               'external_ip':'external_ip',
               'aws_asg':'aws_asg'
            }
    print(tabulate(data, headers=headers))

def gcp():
    pass

def azure():
    nodes_data = kubectl_get_nodes()


    # Step  3: Extract the required information
    data = []
    for node in nodes_data['items']:
        node_info = get_node_info(node, 'azure')
        data.append(node_info)

    # Step  4: Format the output as a table
    headers = {'name':'name',
               'azure_instance_type':'azure_instance_type',
               'status':'status',
               'age':'age',
               'os':'os',
               'version':'version',
               'internal_ip':'internal_ip',
               'external_ip':'external_ip',
            }
    print(tabulate(data, headers=headers))

def main():
    script_name = os.path.basename(sys.argv[0])
    provider = script_name.split('-')[-1]
    if provider == 'aws':
        aws()
    elif provider == 'gcp':
        gcp()
    elif provider == 'azure':
        azure()
    else:
        print("Unsupported cloud provider. Supported: aws, gcp, azure")
        sys.exit(1)

if __name__ == '__main__':
    main()
