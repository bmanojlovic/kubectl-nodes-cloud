Installation Instructions:
===
1. Create a virtual environment for kubectl-node-cloud:
   python3 -m venv ~/.virtualenvs/kubectl-node-cloud

2. Activate the virtual environment:
   . ~/.virtualenvs/kubectl-node-cloud/bin/activate

3. Build the package:
   python setup.py build

4. Install the package:
   python setup.py install

5. Use the tool to interact with AWS:
   kubectl-node-aws

6. Use the tool to interact with GCP:
   kubectl-node-gcp

7. Use the tool to interact with Azure:
   kubectl-node-azure                                                                            
                                                                                                 
8. Copy the wrapper script to your bin directory:
   cp -av kubectl-node-cloud-wrapper ~/bin/

9. Create symlinks for the wrapper script:
   ln -sf ~/bin/kubectl-node-cloud-wrapper ~/bin/kubectl-node-aws
   ln -sf ~/bin/kubectl-node-cloud-wrapper ~/bin/kubectl-node-azure
   ln -sf ~/bin/kubectl-node-cloud-wrapper ~/bin/kubectl-node-gcp

10. To deactivate the virtual environment:
   deactivate

Notes:
===
Replace 'k' with 'kubectl' when using the commands if 'k' is not aliased to 'kubectl'.

Wrapper should find correct venv and run python inside of it now

