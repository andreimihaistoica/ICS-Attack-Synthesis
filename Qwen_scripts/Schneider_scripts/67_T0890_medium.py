import socket
import subprocess

def find_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    
    # List to store potential PLC IP addresses
    potential_plc_ips = []
    
    # Scan the subnet for devices
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Use ping to check if the IP is responsive
            response = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if response.returncode == 0:
                # Check if the device is a Schneider Electric TM221CE16R PLC
                # This is a placeholder for actual identification logic
                # You may need to use specific protocols or identifiers
                potential_plc_ips.append(ip)
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
    
    return potential_plc_ips

def main():
    print("Scanning network for Schneider Electric TM221CE16R PLC...")
    plc_ips = find_plc_ip()
    
    if plc_ips:
        print("Potential PLC IP addresses found:")
        for ip in plc_ips:
            print(ip)
    else:
        print("No PLCs found on the network.")

if __name__ == "__main__":
    main()