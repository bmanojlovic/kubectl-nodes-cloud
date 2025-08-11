"""Tests for context functionality."""

import unittest
from unittest.mock import patch, MagicMock

from kubectl_node.utils import kubectl_get_nodes, get_current_context, list_contexts
from kubectl_node.exceptions import KubectlCommandError


class TestContext(unittest.TestCase):
    """Test context functionality."""
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_with_context(self, mock_popen):
        """Test kubectl command with specific context."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('{"items": []}', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = kubectl_get_nodes(context="test-context")
        
        # Verify the command includes context
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertIn("--context", call_args)
        self.assertIn("test-context", call_args)
        self.assertEqual(result, {"items": []})
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_without_context(self, mock_popen):
        """Test kubectl command without context."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('{"items": []}', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = kubectl_get_nodes()
        
        # Verify the command doesn't include context
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        self.assertNotIn("--context", call_args)
        self.assertEqual(result, {"items": []})
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_kubectl_get_nodes_invalid_context(self, mock_popen):
        """Test kubectl command with invalid context."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error: context "invalid" not found')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        with self.assertRaises(KubectlCommandError) as cm:
            kubectl_get_nodes(context="invalid")
        
        self.assertIn("Context 'invalid' not found", str(cm.exception))
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_get_current_context_success(self, mock_popen):
        """Test getting current context successfully."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('test-context\n', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = get_current_context()
        
        self.assertEqual(result, "test-context")
        mock_popen.assert_called_once_with(
            ["kubectl", "config", "current-context"],
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
            text=True
        )
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_get_current_context_failure(self, mock_popen):
        """Test getting current context when it fails."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error: no context set')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = get_current_context()
        
        self.assertEqual(result, "unknown")
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_list_contexts_success(self, mock_popen):
        """Test listing contexts successfully."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('context1\ncontext2\ncontext3\n', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = list_contexts()
        
        self.assertEqual(result, ['context1', 'context2', 'context3'])
        mock_popen.assert_called_once_with(
            ["kubectl", "config", "get-contexts", "-o", "name"],
            stdout=unittest.mock.ANY,
            stderr=unittest.mock.ANY,
            text=True
        )
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_list_contexts_failure(self, mock_popen):
        """Test listing contexts when it fails."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', 'error: no contexts')
        mock_process.returncode = 1
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = list_contexts()
        
        self.assertEqual(result, [])
    
    @patch('kubectl_node.utils.subprocess.Popen')
    def test_list_contexts_empty(self, mock_popen):
        """Test listing contexts when output is empty."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ('', '')
        mock_process.returncode = 0
        mock_popen.return_value.__enter__.return_value = mock_process
        
        result = list_contexts()
        
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
