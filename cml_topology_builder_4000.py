import os
import requests
from jinja2 import Environment, FileSystemLoader

# Environment variables
def get_env_or_ask(var_name, prompt):
    value = os.getenv(var_name)
    if value is None:
        value = input(prompt)
    return value

# Get NETBOX_URL and NETBOX_TOKEN, ask for them if they're not set
NETBOX_URL = get_env_or_ask('NETBOX_URL', 'Please enter NETBOX_URL: ')
NETBOX_TOKEN = get_env_or_ask('NETBOX_TOKEN', 'Please enter NETBOX_TOKEN: ')
# Headers for NetBox API
HEADERS = {'Authorization': f'Token {NETBOX_TOKEN}', 'Content-Type': 'application/json', 'Accept': 'application/json'}

def get_netbox_data(endpoint):
    """
    Generic function to fetch data from NetBox's API.
    """
    try:
        full_url = f"{NETBOX_URL}/api/{endpoint}"
        response = requests.get(full_url, headers=HEADERS, verify=True)  # Adjust verify as needed
        response.raise_for_status()  # Will raise an HTTPError for bad requests
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err} for URL: {full_url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
    return None

def process_devices(devices):
    """
    Processes devices data to match the Jinja2 template structure.
    Adds a loopback interface to routers and switches, and handles slot numbering for physical interfaces.
    """
    processed_devices = []
    device_id_counter = 0
    for device in devices.get('results', []):
        # Fetch configuration templates (assumes templates are named after the device)
        config_template = get_netbox_data(f"extras/config-templates/?name={device['name']}")
        template_content = config_template['results'][0]['template_code'] if config_template['results'] else "No configuration"
        
        # Map device type to node definition
        node_definition = map_device_type_to_node_definition(device['device_role']['name'])

        # Initialize interfaces list, add loopback interface for routers and switches
        interfaces = []

        # Process and append physical interfaces for the device
        physical_interfaces = process_interfaces(get_netbox_data(f"dcim/interfaces?device_id={device['id']}"), node_definition)
        interfaces.extend(physical_interfaces)

        device_info = {
            'label': device['name'],
            'node_definition': node_definition,
            'configuration': template_content,
            'interfaces': interfaces,
            'id': f"n{device_id_counter}",
        }
        processed_devices.append(device_info)
        device_id_counter += 1
    return processed_devices

def process_interfaces(interfaces_data, node_definition):
    processed_interfaces = []
    interface_counter = 0  # Initialize interface counter for each device

    # First, check if we need to add a loopback interface for specific node definitions
    if node_definition in ['iosv', 'iosvl2']:
        processed_interfaces.append({
            'id': f"i{interface_counter}",  # Assign 'i0' for the loopback interface if needed
            'label': 'Loopback0',
            'type': 'loopback',
        })
        interface_counter += 1  # Increment counter after adding loopback

    for interface in interfaces_data.get('results', []):
        if 'loopback' in interface['name'].lower():
            # Skip directly adding loopback interfaces here since it's either added above or not needed
            continue

        # For physical interfaces, increment counter first if needed
        interface_id = f"i{interface_counter}"
        processed_interfaces.append({
            'id': interface_id,  # Use the updated counter for ID
            'label': interface['name'],
            'type': 'physical',
            'slot': interface_counter - 1 if node_definition in ['iosv', 'iosvl2'] else interface_counter,  # Correct slot assignment
        })
        interface_counter += 1  # Increment counter for each physical interface

    return processed_interfaces


def map_device_type_to_node_definition(device_role):
    """
    Maps device type to a node definition based on simplified logic.
    """
    mappings = {
        'Router': 'iosv',       
        'Switch': 'iosvl2',     
        'Server': 'alpine',     
    }
    return mappings.get(device_role, 'external_connector')  # Default to 'External Connector'

def render_topology_template(devices, links):
    """
    Renders the topology using the Jinja2 template with the given devices and links data.
    """
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('topology_template.j2')
    
    # Pass both devices and links to the template
    rendered_topology = template.render(nodes=devices, links=links)

    # Save or process the rendered topology as needed
    with open('rendered_topology.yaml', 'w') as f:
        f.write(rendered_topology)

def get_cabling_data():
    """
    Fetch cabling data from NetBox.
    """
    return get_netbox_data("dcim/cables")

def process_links(cabling_data, processed_devices):
    links = []

    for cable in cabling_data.get('results', []):
        # Extract device and interface names for A and B terminations
        a_device_name = cable['a_terminations'][0]['object']['device']['name']
        a_interface_name = cable['a_terminations'][0]['object']['name']
        b_device_name = cable['b_terminations'][0]['object']['device']['name']
        b_interface_name = cable['b_terminations'][0]['object']['name']

        # Find the corresponding processed devices and interfaces
        a_device, a_interface = find_device_and_interface_by_name(a_device_name, a_interface_name, processed_devices)
        b_device, b_interface = find_device_and_interface_by_name(b_device_name, b_interface_name, processed_devices)

        if a_device and b_device and a_interface and b_interface:
            link = {
                'id': f"l{cable['id']}",
                'n1': a_device['id'],  # Use the processed device ID
                'n2': b_device['id'],  # Use the processed device ID
                'i1': a_interface['id'],  # Use the sequential interface ID
                'i2': b_interface['id'],  # Use the sequential interface ID
                'label': f"Cable {cable['id']}",
            }
            links.append(link)

    return links


def find_device_and_interface_by_name(device_name, interface_name, processed_devices):
    for device in processed_devices:
        if device['label'] == device_name:
            for interface in device['interfaces']:
                if interface['label'] == interface_name:
                    return device, interface
    return None, None


if __name__ == "__main__":
    devices = get_netbox_data("dcim/devices")
    processed_devices = process_devices(devices)
    cables = get_cabling_data()
    processed_links = process_links(cables, processed_devices)
    render_topology_template(processed_devices, processed_links)
    print("Topology rendering completed.")
