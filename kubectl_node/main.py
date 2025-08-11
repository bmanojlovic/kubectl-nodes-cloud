"""Main module for kubectl-node-cloud."""

import sys
import time
import argparse
from tabulate import tabulate

from .utils import kubectl_get_nodes, get_current_context, list_contexts
from .providers import ProviderManager
from .exceptions import KubectlNodeError


def display_nodes(context=None, clear_screen=False):
    """Display Kubernetes nodes with cloud provider information."""
    if clear_screen:
        # Clear screen for watch mode
        print("\033[2J\033[H", end="")
    
    try:
        # Get nodes data from kubectl
        nodes_data = kubectl_get_nodes(context=context)
        nodes = nodes_data.get("items", [])
        
        # Display context information
        current_context = context or get_current_context()
        if not clear_screen:  # Only show context header in non-watch mode initially
            print(f"Context: {current_context}")
            print()
        
        if not nodes:
            print("No nodes found in the cluster.")
            return
        
        # Initialize provider manager
        provider_manager = ProviderManager()
        
        # Get all headers needed for this set of nodes
        headers = provider_manager.get_all_headers(nodes)
        
        # Extract information for each node
        table_data = []
        for node in nodes:
            row_data = provider_manager.get_node_info(node, headers)
            table_data.append(row_data)
        
        # Display the table
        print(tabulate(table_data, headers=headers, tablefmt="plain"))
        
        if clear_screen:
            # Add timestamp and context for watch mode
            print(f"\nContext: {current_context}")
            print(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KubectlNodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        if hasattr(e, 'stderr') and e.stderr:
            print(f"kubectl stderr: {e.stderr}", file=sys.stderr)
        if not clear_screen:  # Don't exit in watch mode
            sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if not clear_screen:  # Don't exit in watch mode
            sys.exit(1)


def watch_nodes(context=None, interval=2):
    """Watch nodes and refresh display periodically."""
    current_context = context or get_current_context()
    print(f"Watching nodes in context '{current_context}' (press Ctrl+C to stop)...")
    print(f"Refresh interval: {interval} seconds\n")
    
    try:
        while True:
            display_nodes(context=context, clear_screen=True)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nWatch stopped.")
        sys.exit(0)


def list_available_contexts():
    """List available kubectl contexts."""
    contexts = list_contexts()
    current = get_current_context()
    
    if not contexts:
        print("No contexts found. Make sure kubectl is configured.")
        return
    
    print("Available contexts:")
    for ctx in contexts:
        marker = " *" if ctx == current else "  "
        print(f"{marker} {ctx}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enhanced kubectl node information with cloud provider details",
        prog="kubectl-node"
    )
    
    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        help="Watch nodes and refresh display periodically"
    )
    
    parser.add_argument(
        "--watch-interval",
        type=int,
        default=2,
        metavar="SECONDS",
        help="Refresh interval for watch mode (default: 2 seconds)"
    )
    
    parser.add_argument(
        "--context",
        type=str,
        metavar="CONTEXT",
        help="Kubectl context to use (default: current context)"
    )
    
    parser.add_argument(
        "--list-contexts",
        action="store_true",
        help="List available kubectl contexts and exit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="kubectl-node-cloud 0.2.0"
    )
    
    return parser.parse_args()


def main():
    """Main entry point for kubectl-node."""
    args = parse_args()
    
    if args.list_contexts:
        list_available_contexts()
        return
    
    if args.watch:
        watch_nodes(context=args.context, interval=args.watch_interval)
    else:
        display_nodes(context=args.context)


if __name__ == "__main__":
    main()
