import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

def discover_plc_ip():
    # Function to discover the PLC's IP address on the network
    print("Discovering PLC IP address...")
    ip_range = "192.168.1.0/24"  # Adjust this to your network range
    discovered_ips = []

    # Use a simple UDP broadcast to discover the PLC
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5)  # Timeout for receiving responses
        sock.sendto(b"DISCOVER", ('255.255.255.255', 102))  # Send broadcast message

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data:
                    discovered_ips.append(addr[0])
            except socket.timeout:
                break

    if discovered_ips:
        print(f"Discovered PLC IP addresses: {discovered_ips}")
        return discovered_ips[0]  # Return the first discovered IP
    else:
        print("No PLC IP addresses found.")
        return None

def get_plc_operating_mode(plc_ip):
    # Function to get the operating mode of the PLC
    print(f"Connecting to PLC at IP: {plc_ip}...")
    try:
        with pycomm3.CipDriver(plc_ip) as driver:
            if driver.open():
                print("Connection successful.")
                operating_mode = driver.get_plc_operating_mode()
                print(f"PLC Operating Mode: {operating_mode}")
            else:
                print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        get_plc_operating_mode(plc_ip)

if __name__ == "__main__":
    main()