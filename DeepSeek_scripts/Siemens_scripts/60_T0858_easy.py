import socket
import requests

# Function to discover PLC's IP address
def discover_plc_ip():
    # Replace with the appropriate broadcast address and port for your network
    broadcast_address = '192.168.1.255'
    port = 44818  # Common port for PLC communication

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for response

    # Send a discovery message (this is a placeholder; replace with actual discovery protocol)
    discovery_message = b"PLC_DISCOVERY"
    sock.sendto(discovery_message, (broadcast_address, port))

    try:
        # Wait for a response from the PLC
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Discovered PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC discovery timed out. Ensure the PLC is connected and reachable.")
        return None
    finally:
        sock.close()

# Function to change PLC operating mode
def change_plc_mode(plc_ip, mode):
    # Replace with the actual API endpoint and mode change command
    api_url = f"http://{plc_ip}/api/mode"
    payload = {"mode": mode}

    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print(f"PLC mode changed to {mode} successfully.")
        else:
            print(f"Failed to change PLC mode. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with PLC: {e}")

# Main script execution
if __name__ == "__main__":
    # Step 1: Discover PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Step 2: Change PLC operating mode (e.g., to "Program" mode)
        new_mode = "Program"  # Replace with the desired mode: "Program", "Run", "Remote", etc.
        change_plc_mode(plc_ip, new_mode)
    else:
        print("PLC IP address not found. Exiting script.")