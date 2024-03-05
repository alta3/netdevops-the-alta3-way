import gitlab
import os
import json

# This script expects  that you have: 
# 1) A Gitlab Repo to hold the configuarions that has been cloned to your machine 
# 2) A personal access token to that gitlab repo that has been saved as env GL_TOKEN 
# 3) Updated the REPO_ID variable on line 16 to point to your gitlab repo 
# 4) A facts directory holding the facts .json files that is located in the parent directory to the Gitlab Repo directory 
# 5) This script in the Gitlab Repo directory


# Configuration
GL_TOKEN = os.getenv("GL_TOKEN")
GL_URL = "https://gitlab.com"
REPO_ID = "JoeSpizz/router-config-demo"  # Found in the project's homepage URL

gl = gitlab.Gitlab(GL_URL, private_token=GL_TOKEN)
project = gl.projects.get(REPO_ID)

def process_json_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                data = json.load(file)
                hostname = data['ansible_facts'].get('ansible_net_hostname')
                net_config = data['ansible_facts'].get('ansible_net_config')
                # File path in the repo, including hostname as a directory
                file_path = f"router-configs/{hostname}/current_config"
    
                try:
                    # Try to get the file if it exists
                    file = project.files.get(file_path=file_path, ref='main')
                    file.content = net_config
                    file.save(branch='main', commit_message=f'Update config for {hostname}')
                except gitlab.exceptions.GitlabGetError:
                    # If the file doesn't exist, create a new one
                    data = { 
                        'file_path': file_path,
                        'branch': 'main',
                        'content': net_config,
                        'commit_message': f'Create config for {hostname}'
                    }   
                    project.files.create(data)

if __name__ == "__main__":
    process_json_files('../facts/')
