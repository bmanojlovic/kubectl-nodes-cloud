"""Tests for utility functions."""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import json

from kubectl_node.utils import (
    format_timedelta,
    calculate_node_age,
    kubectl_get_nodes,
    get_current_context,
    list_contexts,
    get_node_status,
    get_node_roles,
    get_node_addresses
)
from kubectl_node.exceptions import KubectlCommandError, JSONParseError


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_format_timedelta(self):
        """Test timedelta formatting."""
        # Test days
        td = timedelta(days=5, hours=2, minutes=30)
        self.assertEqual(format_timedelta(td), "5d")
        
        # Test hours
        td = timedelta(hours=3, minutes=45)
        self.assertEqual(format_timedelta(td), "3h")
        
        # Test minutes
        td = timedelta(minutes=25, seconds=30)
        self.assertEqual(format_timedelta(td), "25m")
        
        # Test seconds
        td = timedelta(seconds=45)
        self.assertEqual(format_timedelta(td), "45s")
    
    def test_calculate_node_age(self):
        """Test node age calculation."""
        # Mock current time
        with patch('kubectl_node.utils.datetime') as mock_datetime:
            mock_datetime.strptime.return_value = datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.utcnow.return_value = datetime(2023, 1, 2, 12, 0, 0)
            
            age = calculate_node_age("2023-01-01T12:00:00Z")
            self.assertEqual(age, "1d")
    
    def test_calculate_node_age_invalid(self):
        """Test node age calculation with invalid timestamp."""
        age = calculate_node_age("invalid-timestamp")
        self.assertEqual(age, "Unknown")
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_success(self, mock_popen):
        """Test successful kubectl command execution."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('{"items": []}', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = kubectl_get_nodes()
        self.assertEqual(result, {"items": []})
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_with_context(self, mock_popen):
        """Test kubectl command execution with context."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('{"items": []}', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = kubectl_get_nodes(context="test-context")
        
        # Verify context was included in command
        call_args = mock_popen.call_args[0][0]
        self.assertIn("--context", call_args)
        self.assertIn("test-context", call_args)
        self.assertEqual(result, {"items": []})
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_command_error(self, mock_popen):
        """Test kubectl command execution failure."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'kubectl error')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        with self.assertRaises(KubectlCommandError):
            kubectl_get_nodes()
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_context_error(self, mock_popen):
        """Test kubectl command execution with context error."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error: context "invalid" not found')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        with self.assertRaises(KubectlCommandError) as cm:
            kubectl_get_nodes(context="invalid")
        
        self.assertIn("Context 'invalid' not found", str(cm.exception))
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_json_error(self, mock_popen):
        """Test kubectl command with invalid JSON."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('invalid json', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        with self.assertRaises(JSONParseError):
            kubectl_get_nodes()
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_get_current_context_success(self, mock_popen):
        """Test getting current context successfully."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('test-context\n', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = get_current_context()
        self.assertEqual(result, "test-context")
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_get_current_context_failure(self, mock_popen):
        """Test getting current context failure."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'no context')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = get_current_context()
        self.assertEqual(result, "unknown")
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_list_contexts_success(self, mock_popen):
        """Test listing contexts successfully."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('ctx1\nctx2\nctx3\n', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = list_contexts()
        self.assertEqual(result, ['ctx1', 'ctx2', 'ctx3'])
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_list_contexts_failure(self, mock_popen):
        """Test listing contexts failure."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = list_contexts()
        self.assertEqual(result, [])
    
    def test_get_node_status_ready(self):
        """Test node status extraction for ready node."""
        node = {
            "status": {
                "conditions": [
                    {"type": "Ready", "status": "True"}
                ]
            },
            "spec": {}
        }
        
        status = get_node_status(node)
        self.assertEqual(status, "Ready")
    
    def test_get_node_status_not_ready(self):
        """Test node status extraction for not ready node."""
        node = {
            "status": {
                "conditions": [
                    {"type": "Ready", "status": "False"}
                ]
            },
            "spec": {}
        }
        
        status = get_node_status(node)
        self.assertEqual(status, "NotReady")
    
    def test_get_node_status_scheduling_disabled(self):
        """Test node status with scheduling disabled."""
        node = {
            "status": {
                "conditions": [
                    {"type": "Ready", "status": "True"}
                ]
            },
            "spec": {"unschedulable": True}
        }
        
        status = get_node_status(node)
        self.assertEqual(status, "Ready,SchedulingDisabled")
    
    def test_get_node_roles(self):
        """Test node roles extraction."""
        node = {
            "metadata": {
                "labels": {
                    "node-role.kubernetes.io/master": "",
                    "node-role.kubernetes.io/worker": "",
                    "other-label": "value"
                }
            }
        }
        
        roles = get_node_roles(node)
        self.assertEqual(roles, "master,worker")
    
    def test_get_node_roles_none(self):
        """Test node roles extraction with no roles."""
        node = {
            "metadata": {
                "labels": {
                    "other-label": "value"
                }
            }
        }
        
        roles = get_node_roles(node)
        self.assertEqual(roles, "<none>")
    
    def test_get_node_addresses(self):
        """Test node address extraction."""
        node = {
            "status": {
                "addresses": [
                    {"type": "InternalIP", "address": "10.0.0.1"},
                    {"type": "ExternalIP", "address": "203.0.113.1"},
                    {"type": "Hostname", "address": "node1"}
                ]
            }
        }
        
        addresses = get_node_addresses(node)
        expected = {
            "INTERNAL-IP": "10.0.0.1",
            "EXTERNAL-IP": "203.0.113.1"
        }
        self.assertEqual(addresses, expected)
    
    def test_get_node_addresses_missing(self):
        """Test node address extraction with missing addresses."""
        node = {
            "status": {
                "addresses": [
                    {"type": "Hostname", "address": "node1"}
                ]
            }
        }
        
        addresses = get_node_addresses(node)
        expected = {
            "INTERNAL-IP": "N/A",
            "EXTERNAL-IP": "N/A"
        }
        self.assertEqual(addresses, expected)


if __name__ == '__main__':
    unittest.main()
