import requests
import os
import gitlab
import base64
# This script expects  that you have: 
# 1) A Gitlab Repo to hold the configuarions that has been cloned to your machine 
# 2) A personal access token to that gitlab repo that has been saved as env GL_TOKEN
# 3) env's set for NETBOX_URL and NETBOX_TOKEN
# 4) Updated the REPO_ID variable on line 18 to point to your gitlab repo 
# 5) A facts directory holding the facts .json files that is located in the parent directory to the Gitlab Repo directory 
# 6) This script in the Gitlab Repo directory


# Load environment variables
NETBOX_URL = os.getenv('NETBOX_URL')
NETBOX_TOKEN = os.getenv('NETBOX_TOKEN')
GL_TOKEN = os.getenv('GL_TOKEN')
GL_URL = "https://gitlab.com"
REPO_ID = "JoeSpizz/router-config-demo"
FACTS_DIR = "../facts/"  # Adjust this path as necessary

# Initialize GitLab
gl = gitlab.Gitlab(GL_URL, private_token=GL_TOKEN)
project = gl.projects.get(REPO_ID)

def find_template_by_name(hostname):
    """Search for an existing template by hostname."""
    response = requests.get(f"{NETBOX_URL}/api/extras/config-templates/?name={hostname}",
                            headers={'Authorization': f'Token {NETBOX_TOKEN}',
                                     'Content-Type': 'application/json',
                                     'Accept': 'application/json',})
    if response.status_code == 200 and response.json()['count'] > 0:
        return response.json()['results'][0]  # Return the first matching template
    return None

def process_config_for_hostname(hostname):
    """Process configuration for a given hostname."""
    file_path = f"router-configs/{hostname}/current_config"
    try:
        file = project.files.get(file_path=file_path, ref='main')
        config_data = base64.b64decode(file.content).decode('utf-8')
    except gitlab.exceptions.GitlabGetError:
        print(f"Failed to retrieve configuration for {hostname}")
        return

    headers = {
        'Authorization': f'Token {NETBOX_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    data = {
        "name": hostname,
        "template_code": config_data,
    }

    existing_template = find_template_by_name(hostname)

    if existing_template:
        response = requests.patch(f"{NETBOX_URL}/api/extras/config-templates/{existing_template['id']}/",
                                  headers=headers, json=data)
    else:
        response = requests.post(f"{NETBOX_URL}/api/extras/config-templates/", headers=headers, json=data)

    if response.status_code in [200, 201, 204]:
        print(f"Configuration successfully uploaded for {hostname}.")
    else:
        print(f"Failed to upload configuration for {hostname}: {response.text}")

# Iterate over every file in the facts directory
for filename in os.listdir(FACTS_DIR):
    if filename.endswith(".json"):  # Ensure it's a JSON file
        hostname = filename[:-11]  # Assuming the filename is the hostname.json
        process_config_for_hostname(hostname)
