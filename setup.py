from setuptools import setup, find_packages

setup(
    name='kubectl-node',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'tabulate',
    ],
    scripts=['kubectl-node-cloud'],
)
