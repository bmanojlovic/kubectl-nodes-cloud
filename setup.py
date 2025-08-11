"""Setup configuration for kubectl-node-cloud."""

from setuptools import setup, find_packages

setup(
    name="kubectl-node-cloud",
    version="0.2.0",
    description="Enhanced kubectl node information with cloud provider details",
    packages=find_packages(),
    install_requires=[
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "kubectl-node=kubectl_node:main",
        ],
    },
    python_requires=">=3.6",
    author="kubectl-node-cloud contributors",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
)
