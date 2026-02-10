from scapy.all import ARP, Ether, srp
import socket

def find_plc_ip():
    # Define the IP range to scan (e.g., '192.168.1.1/24')
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP addresses of devices that responded
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a specific MAC address prefix (e.g., '00:1D:9C')
    plc_mac_prefix = "00:1D:9C"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            print(f"PLC found at IP: {device['ip']}")
            return device['ip']
    
    print("PLC not found in the network.")
    return None

def activate_firmware_update_mode(plc_ip):
    # Define the command to activate firmware update mode
    command = "ACTIVATE_FIRMWARE_UPDATE_MODE"
    
    # Create a socket connection to the PLC
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((plc_ip, 502))  # Assuming the PLC uses port 502 for Modbus TCP
            s.sendall(command.encode())
            print(f"Sent command to PLC at {plc_ip}: {command}")
    except Exception as e:
        print(f"Failed to send command to PLC: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        activate_firmware_update_mode(plc_ip)