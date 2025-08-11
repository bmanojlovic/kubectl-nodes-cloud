"""Tests for main module functionality."""

import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

from kubectl_node.main import parse_args, main


class TestMain(unittest.TestCase):
    """Test main module functionality."""
    
    def test_parse_args_default(self):
        """Test default argument parsing."""
        with patch('sys.argv', ['kubectl-node']):
            args = parse_args()
            self.assertFalse(args.watch)
            self.assertEqual(args.watch_interval, 2)
            self.assertIsNone(args.context)
            self.assertFalse(args.list_contexts)
    
    def test_parse_args_watch(self):
        """Test watch argument parsing."""
        with patch('sys.argv', ['kubectl-node', '-w']):
            args = parse_args()
            self.assertTrue(args.watch)
            self.assertEqual(args.watch_interval, 2)
            self.assertIsNone(args.context)
    
    def test_parse_args_watch_long(self):
        """Test long watch argument parsing."""
        with patch('sys.argv', ['kubectl-node', '--watch']):
            args = parse_args()
            self.assertTrue(args.watch)
            self.assertEqual(args.watch_interval, 2)
    
    def test_parse_args_watch_interval(self):
        """Test watch interval argument parsing."""
        with patch('sys.argv', ['kubectl-node', '-w', '--watch-interval', '5']):
            args = parse_args()
            self.assertTrue(args.watch)
            self.assertEqual(args.watch_interval, 5)
    
    def test_parse_args_context(self):
        """Test context argument parsing."""
        with patch('sys.argv', ['kubectl-node', '--context', 'test-context']):
            args = parse_args()
            self.assertEqual(args.context, 'test-context')
            self.assertFalse(args.watch)
    
    def test_parse_args_list_contexts(self):
        """Test list-contexts argument parsing."""
        with patch('sys.argv', ['kubectl-node', '--list-contexts']):
            args = parse_args()
            self.assertTrue(args.list_contexts)
    
    def test_parse_args_combined(self):
        """Test combined arguments parsing."""
        with patch('sys.argv', ['kubectl-node', '-w', '--context', 'prod', '--watch-interval', '10']):
            args = parse_args()
            self.assertTrue(args.watch)
            self.assertEqual(args.context, 'prod')
            self.assertEqual(args.watch_interval, 10)
    
    def test_parse_args_version(self):
        """Test version argument parsing."""
        with patch('sys.argv', ['kubectl-node', '--version']):
            with self.assertRaises(SystemExit) as cm:
                parse_args()
            self.assertEqual(cm.exception.code, 0)
    
    def test_parse_args_help(self):
        """Test help argument parsing."""
        with patch('sys.argv', ['kubectl-node', '--help']):
            with self.assertRaises(SystemExit) as cm:
                parse_args()
            self.assertEqual(cm.exception.code, 0)
    
    @patch('kubectl_node.main.display_nodes')
    @patch('kubectl_node.main.parse_args')
    def test_main_default(self, mock_parse_args, mock_display_nodes):
        """Test main function with default arguments."""
        mock_args = MagicMock()
        mock_args.watch = False
        mock_args.context = None
        mock_args.list_contexts = False
        mock_parse_args.return_value = mock_args
        
        main()
        
        mock_display_nodes.assert_called_once_with(context=None)
    
    @patch('kubectl_node.main.display_nodes')
    @patch('kubectl_node.main.parse_args')
    def test_main_with_context(self, mock_parse_args, mock_display_nodes):
        """Test main function with context."""
        mock_args = MagicMock()
        mock_args.watch = False
        mock_args.context = 'test-context'
        mock_args.list_contexts = False
        mock_parse_args.return_value = mock_args
        
        main()
        
        mock_display_nodes.assert_called_once_with(context='test-context')
    
    @patch('kubectl_node.main.watch_nodes')
    @patch('kubectl_node.main.parse_args')
    def test_main_watch(self, mock_parse_args, mock_watch_nodes):
        """Test main function with watch mode."""
        mock_args = MagicMock()
        mock_args.watch = True
        mock_args.watch_interval = 3
        mock_args.context = 'prod'
        mock_args.list_contexts = False
        mock_parse_args.return_value = mock_args
        
        main()
        
        mock_watch_nodes.assert_called_once_with(context='prod', interval=3)
    
    @patch('kubectl_node.main.list_available_contexts')
    @patch('kubectl_node.main.parse_args')
    def test_main_list_contexts(self, mock_parse_args, mock_list_contexts):
        """Test main function with list-contexts."""
        mock_args = MagicMock()
        mock_args.list_contexts = True
        mock_parse_args.return_value = mock_args
        
        main()
        
        mock_list_contexts.assert_called_once()


if __name__ == '__main__':
    unittest.main()
