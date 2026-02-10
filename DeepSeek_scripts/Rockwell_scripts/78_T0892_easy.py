import os
import socket
import subprocess
from time import sleep

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    # Replace with the expected PLC MAC address or a known identifier
    plc_mac = "00:1D:9C:C7:B0:70"  # Example MAC address
    print("Scanning network for PLC...")
    
    # Use ARP to find devices on the network
    arp_output = subprocess.check_output(["arp", "-a"]).decode("utf-8")
    
    # Search for the PLC's MAC address in the ARP table
    for line in arp_output.splitlines():
        if plc_mac.lower() in line.lower():
            ip_address = line.split()[0]  # Extract the IP address
            print(f"Found PLC at IP: {ip_address}")
            return ip_address
    
    print("PLC not found on the network.")
    return None

# Function to change the PLC credentials
def change_plc_credentials(ip_address, new_username, new_password):
    print(f"Attempting to change credentials on PLC at {ip_address}...")
    
    # Simulate a connection to the PLC (replace with actual PLC API or protocol)
    try:
        # Example: Using a socket to simulate communication
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.connect((ip_address, 502))  # Default Modbus port
        
        # Send a command to change credentials
        # Replace with the actual command for your PLC
        command = f"CHANGE_CREDENTIALS {new_username} {new_password}"
        plc_socket.send(command.encode())
        
        # Wait for a response
        response = plc_socket.recv(1024).decode()
        print(f"Response from PLC: {response}")
        
        plc_socket.close()
        print("Credentials changed successfully.")
    except Exception as e:
        print(f"Failed to change credentials: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Change the PLC credentials
        new_username = "admin"  # Replace with the desired username
        new_password = "newSecurePassword123"  # Replace with the desired password
        change_plc_credentials(plc_ip, new_username, new_password)
    else:
        print("Unable to proceed without PLC IP address.")