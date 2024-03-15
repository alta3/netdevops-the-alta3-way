#!/bin/bash

# Check for environment variable to be set before proceeding
if [[ -z "$NETBOX_URL" ]]; then
    echo "Environment variable 'NETBOX_URL' does not exist. Exiting."
    echo "Please set the environment variable with 'export NETBOX_URL=<your netbox URL>'"
    echo "and then run this script again."
    exit 1
else
    # NETBOX_URL var is set
    echo -e "NETBOX_URL is set to: \n$NETBOX_URL"
    printf "\n"
fi

url_set_to=$NETBOX_URL
sleep 2

# Regular expression pattern to match the URL format
expected_pattern="^https://netbox-[[:alnum:]-]+\.live\.alta3\.com$"

if [[ $url_set_to =~ $expected_pattern ]]; then
    echo "URL is in the correct format, continuing.."
else
    echo "URL does not match the expected format."
    echo "Run export NETBOX_URL=https://netbox-$(hostname -d).live.alta3.com"
    echo "and try the rescue.sh script once more."
fi
sleep 2

# Install necessary requirements for resetting netbox
python3 -m pip install paramiko

# Make a directory where the reset will be looking for the ansible playbook
mkdir -p ~/ansible

# Copy the script and playbook to your home directory for an easier way to find them if needed
cp ~/git/netdevops-the-alta3-way/labs/ansible-netbox-cml/netbox_reset.py ~/netbox_reset.py
cp ~/git/netdevops-the-alta3-way/labs/ansible-netbox-cml/minimum-netbox.yml ~/ansible/minimum-netbox.yml

## Run the netbox_reset.py script, which runs the minimum-netbox.yml playbook after resetting netbox
## Make sure to log back into netbox when prompted for the API Token and create a new token
## to populate the value for the prompt "Enter the new NetBox API token:"
## TODO: either make this an api call to create the token and populate or drop this.

echo "Once you see output that says 'NetBox reset', switch"
echo "over to your netbox tab and follow the below instructions"
echo "....................................."
echo "....................................."
echo "1. Log in as student with password alta3"
echo "2. From the menu on the left, select Admin > Api Tokens"
echo "   and click the green + sign next to it."
echo "3. Select student from dropdown for user."
echo "4. Ensure Write enabled box is checked."
echo "5. Copy the key (this is your last chance to do so)"
echo "6. Click the Create button to actually create the token."
echo "7. Switch back to your TMUX"
echo "....................................."
echo "....................................."

read -p "Press Enter to continue, above are the steps you need to take when the script runs..."

printf "\n"
echo "When you see the prompt 'Enter the new NetBox API token:'"
echo "paste the token in that you copied from netbox and hit enter."
printf "\n"

read -p "Press Enter to continue... The script will now execute!"


python3 ~/netbox_reset.py
