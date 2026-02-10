import socket
import netifaces as ni
import requests
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':  # Exclude loopback address
                # Try to connect to the PLC
                try:
                    # Example: Check if the PLC is responding to a simple HTTP request
                    response = requests.get(f'http://{ip}:80', timeout=2)
                    if response.status_code == 200:
                        print(f"PLC found at IP: {ip}")
                        return ip
                except requests.exceptions.RequestException:
                    continue
        except KeyError:
            continue
    
    print("PLC not found on the network.")
    return None

# Function to restart the PLC
def restart_plc(plc_ip):
    if plc_ip is None:
        print("PLC IP address not found. Cannot proceed with restart.")
        return
    
    # Example: Using a simple HTTP request to restart the PLC
    # Note: This is a placeholder. The actual method to restart the PLC may vary.
    try:
        response = requests.post(f'http://{plc_ip}/api/restart', timeout=5)
        if response.status_code == 200:
            print("PLC restart command sent successfully.")
        else:
            print(f"Failed to send restart command. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send restart command: {e}")

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Wait for a few seconds to ensure the PLC is ready
        time.sleep(5)
        
        # Restart the PLC
        restart_plc(plc_ip)

if __name__ == "__main__":
    main()