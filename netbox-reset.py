# THIS CODE NEEDS TO ADD commands to install requirements.txt then run manage.py migrate before netbox will be back up. Right now it kill snetbox. 

import paramiko

# SSH Connection Detail - Just the host
host = 'netbox'

# Environment Variables
env_vars = {
    'DJANGO_SUPERUSER_USERNAME': 'student',
    'DJANGO_SUPERUSER_EMAIL': 'email@alta3.com',
    'DJANGO_SUPERUSER_PASSWORD': 'alta3',
}

# Function to execute commands over SSH
def ssh_execute(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host)
    stdin, stdout, stderr = ssh.exec_command(command)
    response = stdout.read() + stderr.read()
    ssh.close()
    return response

# Main function
def main():
    # Terminate connections and reset the database
    ssh_execute("sudo -u postgres psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'netbox';\"")
    ssh_execute("sudo -u postgres psql -c \"DROP DATABASE IF EXISTS netbox;\"")
    ssh_execute("sudo -u postgres psql -c \"CREATE DATABASE netbox;\"")

    # Set environment variables and create superuser
    for key, value in env_vars.items():
        ssh_execute(f"export {key}='{value}'")
    ssh_execute("python3 /opt/netbox/netbox/manage.py createsuperuser --noinput")

    print("NetBox reset")

if __name__ == "__main__":
    main()
