import requests
import os
import gitlab
import base64
import subprocess

# This script expects  that you have: 
# 1) A Gitlab Repo to hold the configuarions that has been cloned to your machine 
# 2) A personal access token to that gitlab repo that has been saved as env GL_TOKEN
# 3) env's set for NETBOX_URL and NETBOX_TOKEN
# 4) Updated the REPO_ID variable on line 19 to point to your gitlab repo 
# 5) This script in the Gitlab Repo directory

# Load environment variables
NETBOX_URL = os.getenv('NETBOX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')
GL_TOKEN = os.getenv('GL_TOKEN')
GL_URL = "https://gitlab.com"
REPO_ID = "JoeSpizz/router-config-demo"
inventory_path = os.path.join(script_dir, "inventory.ini")
playbook_path = os.path.join(script_dir, "push_changes_playbook.yml")
ssh_config_path = os.path.expanduser("~/.ssh/config")

# Initialize GitLab
gl = gitlab.Gitlab(GL_URL, private_token=GL_TOKEN)
project = gl.projects.get(REPO_ID)

# User input for hostname
hostname = input("Enter the device hostname: ")

def execute_ansible_playbook(hostname, inventory_path, playbook_path, ssh_config_path):
    command = [
        "ansible-playbook",
        "-i", inventory_path,
        "-e", f"target={hostname}",
        "--ssh-common-args='-F {ssh_config_path}'",
        playbook_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Ansible playbook executed successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Ansible playbook: {e.stderr}")

def find_template_by_name(hostname):
    """Search for an existing template by hostname."""
    response = requests.get(f"{NETBOX_URL}/api/extras/config-templates/?name={hostname}",
                            headers={'Authorization': f'Token {NETBOX_TOKEN}',
                                     'Content-Type': 'application/json',
                                     'Accept': 'application/json',})
    if response.status_code == 200 and response.json()['count'] > 0:
        return response.json()['results'][0]  # Return the first matching template
    return None

def update_gitlab_file(repo, file_path, content, commit_message):
    """Update or create a file in GitLab repository."""
    try:
        file = repo.files.get(file_path=file_path, ref='main')
        file.content = content
        file.save(branch='main', commit_message=commit_message)
    except gitlab.exceptions.GitlabGetError:
        # If the file does not exist, create it
        repo.files.create({
            'file_path': file_path,
            'branch': 'main',
            'content': content,
            'commit_message': commit_message
        })

# GitLab retrieval
file_path = f"router-configs/{hostname}/next_config"
try:
    file = project.files.get(file_path=file_path, ref='main')
    # Decode the file content from bytes to string
    config_data = base64.b64decode(file.content).decode('utf-8')
except gitlab.exceptions.GitlabGetError:
    print(f"Failed to retrieve configuration for {hostname}")
    exit(1)

# NetBox API push - Ensure the data dictionary is correctly formed for JSON serialization
headers = {
    'Authorization': f'Token {NETBOX_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}
data = {
    "name": f"{hostname}",
    "template_code": config_data,  # Ensure this is a string, not bytes
    # Add other necessary fields as required by your NetBox setup
}

existing_template = find_template_by_name(hostname)
execute_ansible_playbook(hostname, inventory_path, playbook_path, ssh_config_path)
if existing_template:
    # Existing template found, patch it
    response = requests.patch(f"{NETBOX_URL}/api/extras/config-templates/{existing_template['id']}/",
                              headers=headers, json=data)
else:
    # No existing template, create a new one
    response = requests.post(f"{NETBOX_URL}/api/extras/config-templates/", headers=headers, json=data)

if response.status_code in [200, 201, 204]:
    print("Configuration successfully uploaded to NetBox.")
    current_config_path = f"router-configs/{hostname}/current_config"
    update_gitlab_file(project, current_config_path, config_data, f"Update current_config for {hostname}")

    # Blank out specified files
    for file_name in ["next_config", "test_config", "change.txt", "rollback.txt"]:
        file_path = f"router-configs/{hostname}/{file_name}"
        update_gitlab_file(project, file_path, '', f"Reset {file_name} for {hostname}")
    print("gitlab auxillary files reset")
else:
    print(f"Failed to upload configuration to NetBox: {response.text}")
