#!/bin/bash
# This script EXPECTS/REQUIRES: The topology file to be on static at the expected place (line 7), the variables on lines 19-23 and 35-39 to be correct, 
# Step 1: Install cisco.cml collection using ansible-galaxy
ansible-galaxy collection install cisco.cml

# Step 2: Download topo.yaml to the home directory
wget https://static.alta3.com/courses/mdd/topo.yaml -O ~/topo.yaml

# Ensure the previous command succeeded before continuing
if [ $? -eq 0 ]; then
    echo "Download succeeded, proceeding with the playbook commands."
else
    echo "Download failed, exiting."
    exit 1
fi

# Step 3: Run special delete command
ansible-playbook cisco.cml.clean -t erase \
-e "cml_host=10.0.0.80" \
-e "cml_username=admin" \
-e "cml_password=Alta3isgreatftw!" \
-e cml_lab_file=~/topo.yaml \
-e cml_lab="Sim-Lab"

# Check if step 3 succeeded
if [ $? -eq 0 ]; then
    echo "Delete operation succeeded, proceeding with the startup command."
else
    echo "Delete operation failed, exiting."
    exit 1
fi

# Step 4: Only after 3 is done, run special start up command
ansible-playbook cisco.cml.build \
-e "cml_host=10.0.0.80" \
-e "cml_username=admin" \
-e "cml_password=Alta3isgreatftw!" \
-e cml_lab_file=~/topo.yaml \
-e cml_lab="Sim-Lab"
