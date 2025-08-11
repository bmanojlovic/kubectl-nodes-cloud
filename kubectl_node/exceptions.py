"""Custom exceptions for kubectl-node-cloud."""


class KubectlNodeError(Exception):
    """Base exception for kubectl-node-cloud errors."""
    pass


class KubectlCommandError(KubectlNodeError):
    """Raised when kubectl command execution fails."""
    
    def __init__(self, message, stderr=None):
        super().__init__(message)
        self.stderr = stderr


class JSONParseError(KubectlNodeError):
    """Raised when JSON parsing fails."""
    
    def __init__(self, message, raw_output=None):
        super().__init__(message)
        self.raw_output = raw_output


class ProviderDetectionError(KubectlNodeError):
    """Raised when cloud provider detection fails."""
    pass


class NodeInfoError(KubectlNodeError):
    """Raised when node information extraction fails."""
    pass
