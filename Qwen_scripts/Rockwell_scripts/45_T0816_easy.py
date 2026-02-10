import socket
import subprocess
import time
from pyModbusTCP.client import ModbusClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    for line in lines:
        if 'dynamic' in line:
            ip = line.split()[0]
            try:
                # Attempt to connect to the IP to see if it's the PLC
                client = ModbusClient(host=ip, port=502, auto_open=True, auto_close=True)
                if client.is_open():
                    print(f"PLC found at IP: {ip}")
                    return ip
            except Exception as e:
                print(f"Error connecting to {ip}: {e}")
    
    print("PLC not found.")
    return None

# Function to restart the PLC
def restart_plc(ip):
    client = ModbusClient(host=ip, port=502, auto_open=True, auto_close=True)
    if client.is_open():
        try:
            # Example: Write a value to a specific register to trigger a restart
            # This is a hypothetical example; the actual register and value will depend on the PLC model
            client.write_single_register(1, 1)
            print(f"Restart command sent to PLC at IP: {ip}")
        except Exception as e:
            print(f"Error sending restart command: {e}")
    else:
        print(f"Failed to connect to PLC at IP: {ip}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Restart the PLC
        restart_plc(plc_ip)
    else:
        print("PLC not found. Aborting.")

if __name__ == "__main__":
    main()