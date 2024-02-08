import paramiko
import os
import subprocess
# SSH Connection Detail - Just the host
host = 'netbox'

# Function to execute commands over SSH
def ssh_execute(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host)
    stdin, stdout, stderr = ssh.exec_command(command)
    response = stdout.read() + stderr.read()
    ssh.close()

    return response.decode()

# Function to prompt for API token and set as an environment variable
def get_and_set_api_token():
    api_token = input("Enter the new NetBox API token: ")
    os.environ['NETBOX_TOKEN'] = api_token

# Function to run the Ansible playbook
def run_ansible_playbook():
    command = "ansible-playbook ~/ansible/minimum-netbox.yml"
    try:
        # Running the command without capturing output to allow real-time progress visibility
        subprocess.run(command, shell=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        # If an error occurs, print the error message and exit
        print(f"Playbook Error: {e}")
        raise
# Main function
def main():
    # Terminate connections to the netbox database
    print("terminating other users")
    ssh_execute("sudo -u postgres psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'netbox';\"")

    # Drop the database, create a new one, create a user, and set ownership
    print("resetting db")
    ssh_execute("sudo -u postgres psql -c \"DROP DATABASE IF EXISTS netbox;\"")
    ssh_execute("sudo -u postgres psql -c \"CREATE DATABASE netbox;\"")
    ssh_execute("sudo -u postgres psql -c \"ALTER DATABASE netbox OWNER TO netbox;\"")

    print("installing requirements")
    # Install local requirements
    ssh_execute("pip install -r /opt/netbox/requirements.txt")

    print("running migrations, this takes ~3 minutes")
    # Run migrations
    ssh_execute("python3 /opt/netbox/netbox/manage.py migrate")

    # Combine commands to ensure environment variables are exported in the same session
    combined_commands = (
        "export DJANGO_SUPERUSER_USERNAME='student' && "
        "export DJANGO_SUPERUSER_EMAIL='email@alta3.com' && "
        "export DJANGO_SUPERUSER_PASSWORD='alta3' && "
        "python3 /opt/netbox/netbox/manage.py createsuperuser --noinput"
    )
    print("creating superuser")
    ssh_execute(combined_commands)

    print("NetBox reset")

    # Get the new API token from the user
    get_and_set_api_token()

    print("running ansible playbook")
    # Run the Ansible playbook
    run_ansible_playbook()

    print("Ansible playbook execution completed")



if __name__ == "__main__":
    main()
