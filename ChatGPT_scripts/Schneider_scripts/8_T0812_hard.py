import socket
from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient

# Configuration: Update the local network interface as needed
LOCAL_IP = "192.168.9.0/24"  # Replace with your network range
DEFAULT_PORT = 502           # Modbus TCP default port
DEFAULT_CREDENTIALS = {
    "username": "admin",     # Hypothetical default username for the PLC
    "password": "admin"      # Hypothetical default password for the PLC
}

def scan_network(ip_range):
    """Scan the local subnet to identify live hosts."""
    print(f"Scanning network {ip_range} for devices...")
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    devices = []
    for element in answered_list:
        devices.append({'ip': element[1].psrc, 'mac': element[1].hwsrc})
    return devices

def find_plc(devices):
    """Filter the devices to find a potential PLC by checking for open Modbus port."""
    print(f"Checking devices for open Modbus port ({DEFAULT_PORT})...")
    plc_ip = None
    for device in devices:
        ip = device['ip']
        try:
            with socket.create_connection((ip, DEFAULT_PORT), timeout=2) as sock:
                print(f"Device {ip} has port {DEFAULT_PORT} open. Potential PLC found.")
                plc_ip = ip
                break
        except (socket.timeout, ConnectionRefusedError):
            continue
    return plc_ip

def attempt_default_credentials(plc_ip):
    """Attempt to connect to the PLC using default credentials."""
    print(f"Attempting to connect to PLC at {plc_ip} with default credentials...")
    client = ModbusClient(host=plc_ip, port=DEFAULT_PORT)

    # NOTE: Modbus does not support native credentials, but this logic represents a placeholder for
    # a PLC that might have a login step in its implementation (e.g., enhanced Modbus protocol or web interface).
    if client.open():
        print(f"[SUCCESS] Connected to PLC at {plc_ip} using Modbus TCP!")
        # Implementation would vary depending on the PLC manufacturer and protocol
        # For example, interacting with registers or function codes here
        # Example Read Coils
        try:
            print("[INFO] Reading coils from address 0...")
            coils = client.read_coils(0, 10)  # Reads 10 coils starting from address 0
            if coils:
                print(f"[INFO] Coils read: {coils}")
            else:
                print("[INFO] No coil data returned.")
        except Exception as e:
            print(f"[ERROR] Failed to read coils: {e}")
    else:
        print(f"[FAILED] Could not connect to PLC at {plc_ip}. Ensure default credentials are correct.")

    client.close()

# Step 1: Scan the network
devices = scan_network(LOCAL_IP)
if not devices:
    print("[ERROR] No devices found on the network.")
    exit()

# Step 2: Identify the PLC
plc_ip = find_plc(devices)
if not plc_ip:
    print("[ERROR] No PLCs found on the network with open Modbus port.")
    exit()

# Step 3: Attempt to connect using default credentials
attempt_default_credentials(plc_ip)