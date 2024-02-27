from setuptools import setup, find_packages

setup(
    name='kubectl-node',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'kubectl-node-aws=kubectl_node:main',
            'kubectl-node-azure=kubectl_node:main',
            'kubectl-node-gcp=kubectl_node:main',
        ],
    },
    scripts=['kubectl-node-cloud'],
)
