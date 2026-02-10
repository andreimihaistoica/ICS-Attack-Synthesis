import snap7
from scapy.all import ARP, Ether, srp
import sys

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    print(f"Scanning network {ip_range} for PLC...")

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assume the PLC has a specific MAC prefix (adjust as needed)
    plc_mac_prefix = "00:1C:1C"  # Example MAC prefix for Siemens PLCs
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            print(f"Found PLC at IP: {device['ip']}")
            return device['ip']

    print("PLC not found on the network.")
    return None

def detect_plc_mode(plc_ip):
    # Create a Snap7 client
    client = snap7.client.Client()

    try:
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)  # IP, Rack, Slot
        print(f"Connected to PLC at {plc_ip}")

        # Get the PLC status
        status = client.get_cpu_state()
        print(f"PLC Status: {status}")

        # Map the status to operating modes
        mode_map = {
            'S7CpuStatusRun': 'Run',
            'S7CpuStatusStop': 'Stop',
            'S7CpuStatusUnknown': 'Unknown',
        }
        return mode_map.get(status, 'Unknown')

    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None
    finally:
        client.disconnect()

if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        sys.exit("PLC IP address not found.")

    # Detect the PLC's operating mode
    mode = detect_plc_mode(plc_ip)
    if mode:
        print(f"PLC Operating Mode: {mode}")
    else:
        print("Failed to detect PLC operating mode.")