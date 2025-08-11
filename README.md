# kubectl-node-cloud

Enhanced kubectl node information with automatic cloud provider detection and cloud-specific details.

## Features

- **Single entry point**: One command that works with any cloud provider
- **Automatic detection**: Automatically detects AWS, Azure, GCP, or generic clusters
- **Rich information**: Shows cloud-specific metadata like instance IDs, zones, and more
- **Clean output**: Well-formatted table output using the same style as kubectl
- **kubectl plugin**: Works as a standard kubectl plugin (`kubectl node`)
- **Watch mode**: Real-time monitoring with `-w` flag
- **Context support**: Use `--context` to specify kubectl context

## Supported Cloud Providers

- **AWS**: Shows instance ID, availability zone, and ASG information
- **Azure**: Shows instance type, resource group, and zone
- **GCP**: Shows instance ID, zone, node pool, and preemptible status
- **Generic**: Works with any Kubernetes cluster

## Installation

### Method 1: Direct Installation (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd kubectl-nodes-cloud

# Install directly with uv
uv tool install .

# Use the tool
kubectl-node
```

### Method 2: Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd kubectl-nodes-cloud

# Install in development mode
make install-dev

# Run tests
make test
```

### Method 3: kubectl Plugin

After installation, the tool automatically works as a kubectl plugin:

```bash
# Use as kubectl plugin (no symlink needed!)
kubectl node

# Watch mode as kubectl plugin
kubectl node -w
```

## Usage

### Basic Usage

```bash
# Show all nodes with cloud provider information
kubectl-node

# Or use as kubectl plugin
kubectl node
```

### Context Support

```bash
# Use specific context
kubectl-node --context production

# List available contexts
kubectl-node --list-contexts

# Watch nodes in specific context
kubectl-node -w --context staging
```

### Watch Mode

```bash
# Watch nodes with default 2-second refresh
kubectl-node -w

# Watch with custom refresh interval
kubectl-node -w --watch-interval 5

# Watch specific context
kubectl-node -w --context production --watch-interval 10

# As kubectl plugin
kubectl node -w --context staging
```

### Command Line Options

```bash
kubectl-node --help

Usage: kubectl-node [-h] [-w] [--watch-interval SECONDS] [--context CONTEXT] [--list-contexts] [--version]

Enhanced kubectl node information with cloud provider details

Options:
  -h, --help            show this help message and exit
  -w, --watch           Watch nodes and refresh display periodically
  --watch-interval SECONDS
                        Refresh interval for watch mode (default: 2 seconds)
  --context CONTEXT     Kubectl context to use (default: current context)
  --list-contexts       List available kubectl contexts and exit
  --version             show program's version number and exit
```

### Example Output

```
Context: production

NAME                                          STATUS   ROLES    AGE   VERSION   INTERNAL-IP    EXTERNAL-IP     OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME   INSTANCE-TYPE   AWS-INSTANCE-ID      AWS-ZONE    AWS-ASG
ip-10-0-1-100.us-west-2.compute.internal    Ready    <none>   5d    v1.28.0   10.0.1.100     54.123.45.67    Amazon Linux 2       5.4.0-1043-aws     containerd://1.6.6  t3.medium      i-1234567890abcdef0  us-west-2a  
ip-10-0-2-200.us-west-2.compute.internal    Ready    master   5d    v1.28.0   10.0.2.200     54.123.45.68    Amazon Linux 2       5.4.0-1043-aws     containerd://1.6.6  t3.large       i-0987654321fedcba0  us-west-2b  
```

### Watch Mode Output

```
Watching nodes in context 'production' (press Ctrl+C to stop)...
Refresh interval: 2 seconds

NAME                        STATUS    ROLES                      AGE    VERSION       INTERNAL-IP    EXTERNAL-IP      OS-IMAGE          KERNEL-VERSION    CONTAINER-RUNTIME           INSTANCE-TYPE
k3s-control-plane-hel1-tfx  Ready     control-plane,etcd,master  442d   v1.32.5+k3s1  10.253.0.101   65.21.55.95      openSUSE MicroOS  6.15.8-1-default  containerd://2.0.5-k3s1.32  cax11
k3s-control-plane-nbg1-ibw  Ready     control-plane,etcd,master  442d   v1.32.5+k3s1  10.254.0.101   49.13.229.173    openSUSE MicroOS  6.15.8-1-default  containerd://2.0.5-k3s1.32  cax11

Context: production
Last updated: 2024-08-10 13:45:23
```

### Context Management

```bash
# List all available contexts
kubectl-node --list-contexts

# Output:
# Available contexts:
#  * current-context
#    staging
#    production
#    development
```

## Development

### Project Structure

```
kubectl-node-cloud/
├── kubectl_node/
│   ├── __init__.py          # Main package
│   ├── main.py              # Main entry point with CLI
│   ├── config.py            # Configuration constants
│   ├── exceptions.py        # Custom exceptions
│   ├── utils.py             # Utility functions
│   └── providers/           # Cloud provider implementations
│       ├── __init__.py
│       ├── base.py          # Base provider class
│       ├── aws.py           # AWS provider
│       ├── azure.py         # Azure provider
│       ├── gcp.py           # GCP provider
│       ├── generic.py       # Generic provider
│       └── manager.py       # Provider manager
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_utils.py
│   ├── test_providers.py
│   ├── test_main.py
│   └── test_context.py      # Context functionality tests
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
├── run_tests.py            # Test runner
├── Makefile                # Development tasks
└── README.md               # This file
```

### Development Commands

```bash
# Install for development
make install-dev

# Run tests
make test

# Demo the tool
make demo

# Watch mode demo
make watch

# Test as kubectl plugin
make plugin-test

# Clean up
make clean
```

### Running Tests

```bash
# Run all tests
make test

# Or manually
python run_tests.py

# Run specific test file
python -m unittest tests.test_context

# Run with verbose output
python -m unittest -v tests.test_main
```

### Adding New Cloud Providers

1. Create a new provider class in `kubectl_node/providers/`
2. Inherit from `BaseProvider`
3. Implement the required methods:
   - `detect(node)`: Return True if this provider matches the node
   - `get_provider_fields(node)`: Return dict of provider-specific fields
   - `get_additional_headers()`: Return list of additional column headers
4. Add the provider to `ProviderManager` in `manager.py`
5. Add tests for the new provider

### Code Quality

The codebase follows these principles:

- **Single Responsibility**: Each class/function has one clear purpose
- **Provider Pattern**: Cloud-specific logic is isolated in provider classes
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Testing**: Unit tests for all major functionality
- **Documentation**: Docstrings and clear variable names

## Requirements

- Python 3.6+
- kubectl (configured and working)
- tabulate package (installed automatically)

## Troubleshooting

### kubectl command not found
Ensure kubectl is installed and in your PATH.

### Permission denied
Make sure you have proper kubectl permissions to list nodes:
```bash
kubectl auth can-i list nodes
```

### No nodes found
Verify your kubectl context is set correctly:
```bash
kubectl config current-context
kubectl get nodes
```

### Context not found
List available contexts and verify the name:
```bash
kubectl-node --list-contexts
kubectl config get-contexts
```

### Plugin not working
After installation with `uv tool install .`, the `kubectl-node` command should be available in your PATH. The kubectl plugin functionality works automatically - no symlinks needed.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.
