import requests
import os
import gitlab
import base64

# Load environment variables
NETBOX_URL = os.getenv('NETBOX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')
GL_TOKEN = os.getenv('GL_TOKEN')
GL_URL = "https://gitlab.com"
REPO_ID = "JoeSpizz/router-config-demo"

# Initialize GitLab
gl = gitlab.Gitlab(GL_URL, private_token=GL_TOKEN)
project = gl.projects.get(REPO_ID)

# User input for hostname
hostname = input("Enter the device hostname: ")

def find_template_by_name(hostname):
    """Search for an existing template by hostname."""
    response = requests.get(f"{NETBOX_URL}/api/extras/config-templates/?name={hostname}",
                            headers={'Authorization': f'Token {NETBOX_TOKEN}',
                                     'Content-Type': 'application/json',
                                     'Accept': 'application/json',})
    if response.status_code == 200 and response.json()['count'] > 0:
        return response.json()['results'][0]  # Return the first matching template
    return None

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
    # Assuming the structure needed by NetBox, this part might need adjustments
    "name": f"{hostname}",
    "template_code": config_data,  # Ensure this is a string, not bytes
    # Add other necessary fields as required by your NetBox setup
}

existing_template = find_template_by_name(hostname)

if existing_template:
    # Existing template found, patch it
    response = requests.patch(f"{NETBOX_URL}/api/extras/config-templates/{existing_template['id']}/",
                              headers=headers, json=data)
else:
    # No existing template, create a new one
    response = requests.post(f"{NETBOX_URL}/api/extras/config-templates/", headers=headers, json=data)

if response.status_code in [200, 201, 204]:
    print("Configuration successfully uploaded to NetBox.")
else:
    print(f"Failed to upload configuration to NetBox: {response.text}")
