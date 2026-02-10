import snap7
import socket
from snap7.util import *
from snap7.types import *
import sys

def discover_plc_ip():
    """
    Discover the PLC's IP address on the network.
    This is a simple implementation and assumes the PLC responds to a ping.
    """
    # Replace with your network range (e.g., '192.168.1.')
    network_range = '192.168.1.'
    for i in range(1, 255):
        ip = network_range + str(i)
        try:
            # Ping the IP to check if the PLC is reachable
            response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
            if response == 0:
                print(f"PLC found at IP: {ip}")
                return ip
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
    print("PLC not found on the network.")
    return None

def restart_plc(plc_ip):
    """
    Restart the PLC using Snap7.
    """
    try:
        # Create a Snap7 client
        client = snap7.client.Client()
        
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)  # IP, Rack, Slot
        
        # Send a command to restart the PLC
        # This is a placeholder for the actual command to restart the PLC
        # The specific command depends on the PLC's firmware and configuration
        # For Siemens S7-1200, you might need to write to a specific DB or use a function block
        # Example: Write to a specific memory area to trigger a restart
        client.db_write(db_number=1, start=0, data=bytearray([1]))
        
        print(f"Restart command sent to PLC at {plc_ip}")
        
        # Disconnect from the PLC
        client.disconnect()
    except Exception as e:
        print(f"Error restarting PLC: {e}")

def shutdown_plc(plc_ip):
    """
    Shutdown the PLC using Snap7.
    """
    try:
        # Create a Snap7 client
        client = snap7.client.Client()
        
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)  # IP, Rack, Slot
        
        # Send a command to shutdown the PLC
        # This is a placeholder for the actual command to shutdown the PLC
        # The specific command depends on the PLC's firmware and configuration
        # For Siemens S7-1200, you might need to write to a specific DB or use a function block
        # Example: Write to a specific memory area to trigger a shutdown
        client.db_write(db_number=1, start=0, data=bytearray([0]))
        
        print(f"Shutdown command sent to PLC at {plc_ip}")
        
        # Disconnect from the PLC
        client.disconnect()
    except Exception as e:
        print(f"Error shutting down PLC: {e}")

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Step 2: Restart or Shutdown the PLC
        action = input("Do you want to restart or shutdown the PLC? (restart/shutdown): ").strip().lower()
        
        if action == "restart":
            restart_plc(plc_ip)
        elif action == "shutdown":
            shutdown_plc(plc_ip)
        else:
            print("Invalid action. Please choose 'restart' or 'shutdown'.")
    else:
        print("PLC not found. Exiting.")