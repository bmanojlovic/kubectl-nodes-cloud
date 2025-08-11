"""Tests for cloud provider implementations."""

import unittest
from kubectl_node.providers.aws import AWSProvider
from kubectl_node.providers.azure import AzureProvider
from kubectl_node.providers.gcp import GCPProvider
from kubectl_node.providers.generic import GenericProvider
from kubectl_node.providers.manager import ProviderManager


class TestProviders(unittest.TestCase):
    """Test cloud provider implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.aws_provider = AWSProvider()
        self.azure_provider = AzureProvider()
        self.gcp_provider = GCPProvider()
        self.generic_provider = GenericProvider()
        self.manager = ProviderManager()
    
    def test_aws_provider_detection(self):
        """Test AWS provider detection."""
        # AWS node
        aws_node = {
            "metadata": {
                "labels": {
                    "k8s.io/cloud-provider-aws": "true"
                }
            }
        }
        
        self.assertTrue(self.aws_provider.detect(aws_node))
        self.assertFalse(self.azure_provider.detect(aws_node))
        self.assertFalse(self.gcp_provider.detect(aws_node))
        self.assertTrue(self.generic_provider.detect(aws_node))  # Generic always matches
    
    def test_azure_provider_detection(self):
        """Test Azure provider detection."""
        # Azure node
        azure_node = {
            "metadata": {
                "labels": {
                    "kubernetes.azure.com/cluster": "test-cluster"
                }
            }
        }
        
        self.assertFalse(self.aws_provider.detect(azure_node))
        self.assertTrue(self.azure_provider.detect(azure_node))
        self.assertFalse(self.gcp_provider.detect(azure_node))
        self.assertTrue(self.generic_provider.detect(azure_node))
    
    def test_gcp_provider_detection(self):
        """Test GCP provider detection."""
        # GCP node
        gcp_node = {
            "metadata": {
                "labels": {
                    "cloud.google.com/gke-nodepool": "default-pool"
                }
            }
        }
        
        self.assertFalse(self.aws_provider.detect(gcp_node))
        self.assertFalse(self.azure_provider.detect(gcp_node))
        self.assertTrue(self.gcp_provider.detect(gcp_node))
        self.assertTrue(self.generic_provider.detect(gcp_node))
    
    def test_aws_provider_fields(self):
        """Test AWS provider field extraction."""
        aws_node = {
            "metadata": {
                "labels": {
                    "failure-domain.beta.kubernetes.io/zone": "us-west-2a"
                }
            },
            "spec": {
                "providerID": "aws:///us-west-2a/i-1234567890abcdef0",
                "taints": [
                    {"key": "node.kubernetes.io/unschedulable", "effect": "NoSchedule"},
                    {"key": "custom-taint", "effect": "NoSchedule"}
                ]
            }
        }
        
        fields = self.aws_provider.get_provider_fields(aws_node)
        expected = {
            "AWS-INSTANCE-ID": "i-1234567890abcdef0",
            "AWS-ZONE": "us-west-2a",
            "AWS-ASG": "custom-taint"
        }
        self.assertEqual(fields, expected)
    
    def test_azure_provider_fields(self):
        """Test Azure provider field extraction."""
        azure_node = {
            "metadata": {
                "labels": {
                    "node.kubernetes.io/instance-type": "Standard_D2s_v3",
                    "kubernetes.azure.com/resource-group": "test-rg",
                    "failure-domain.beta.kubernetes.io/zone": "eastus-1"
                }
            }
        }
        
        fields = self.azure_provider.get_provider_fields(azure_node)
        expected = {
            "AZURE-INSTANCE-TYPE": "Standard_D2s_v3",
            "AZURE-RESOURCE-GROUP": "test-rg",
            "AZURE-ZONE": "eastus-1"
        }
        self.assertEqual(fields, expected)
    
    def test_gcp_provider_fields(self):
        """Test GCP provider field extraction."""
        gcp_node = {
            "metadata": {
                "labels": {
                    "cloud.google.com/gke-nodepool": "default-pool",
                    "cloud.google.com/gke-preemptible": "true",
                    "failure-domain.beta.kubernetes.io/zone": "us-central1-a"
                }
            },
            "spec": {
                "providerID": "gce://test-project/us-central1-a/gke-cluster-default-pool-12345678-abcd"
            }
        }
        
        fields = self.gcp_provider.get_provider_fields(gcp_node)
        expected = {
            "GCP-INSTANCE-ID": "gke-cluster-default-pool-12345678-abcd",
            "GCP-ZONE": "us-central1-a",
            "GCP-NODE-POOL": "default-pool",
            "GCP-PREEMPTIBLE": "true"
        }
        self.assertEqual(fields, expected)
    
    def test_generic_provider_fields(self):
        """Test generic provider field extraction."""
        generic_node = {
            "metadata": {
                "labels": {}
            }
        }
        
        fields = self.generic_provider.get_provider_fields(generic_node)
        self.assertEqual(fields, {})
        
        headers = self.generic_provider.get_additional_headers()
        self.assertEqual(headers, [])
    
    def test_provider_manager_detection(self):
        """Test provider manager detection."""
        # Test AWS detection
        aws_node = {
            "metadata": {
                "labels": {
                    "k8s.io/cloud-provider-aws": "true"
                }
            }
        }
        provider = self.manager.detect_provider(aws_node)
        self.assertEqual(provider.name, "aws")
        
        # Test generic fallback
        generic_node = {
            "metadata": {
                "labels": {}
            }
        }
        provider = self.manager.detect_provider(generic_node)
        self.assertEqual(provider.name, "generic")
    
    def test_provider_manager_headers(self):
        """Test provider manager header collection."""
        nodes = [
            {
                "metadata": {
                    "labels": {
                        "k8s.io/cloud-provider-aws": "true"
                    }
                }
            },
            {
                "metadata": {
                    "labels": {
                        "cloud.google.com/gke-nodepool": "default-pool"
                    }
                }
            }
        ]
        
        headers = self.manager.get_all_headers(nodes)
        
        # Should include base headers plus AWS and GCP specific headers
        self.assertIn("NAME", headers)
        self.assertIn("AWS-INSTANCE-ID", headers)
        self.assertIn("GCP-INSTANCE-ID", headers)
        self.assertNotIn("AZURE-INSTANCE-TYPE", headers)


if __name__ == '__main__':
    unittest.main()
