import socket
import requests
import struct

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet and responds to ICMP echo requests (ping)
    network = '192.168.1.0/24'  # Change this to your network
    response = os.system("ping -c 1 " + network)
    if response == 0:
        return network
    else:
        raise Exception("PLC not found on the network")

# Function to connect to the PLC and modify alarm settings
def modify_alarm_settings(plc_ip):
    # Define the URL for the PLC's API (if available)
    plc_url = f"http://{plc_ip}/api/alarm_settings"
    
    # Define the new alarm settings
    new_alarm_settings = {
        "alarm1": {"enabled": False, "threshold": 100},
        "alarm2": {"enabled": False, "threshold": 200}
    }
    
    # Send a POST request to modify the alarm settings
    response = requests.post(plc_url, json=new_alarm_settings)
    
    if response.status_code == 200:
        print("Alarm settings modified successfully")
    else:
        print(f"Failed to modify alarm settings: {response.status_code} - {response.text}")

# Main function
def main():
    try:
        # Find the PLC's IP address
        plc_ip = find_plc_ip()
        print(f"PLC found at IP address: {plc_ip}")
        
        # Modify the alarm settings
        modify_alarm_settings(plc_ip)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()