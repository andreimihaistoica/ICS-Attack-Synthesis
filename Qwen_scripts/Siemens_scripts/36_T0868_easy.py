import socket
import subprocess
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'dynamic' in line:
            ip = line.split()[0]
            try:
                # Attempt to connect to the IP to see if it's the PLC
                client = ModbusTcpClient(ip)
                client.connect()
                if client.is_socket_open():
                    print(f"PLC found at IP: {ip}")
                    return ip
            except ConnectionException:
                continue
            finally:
                client.close()
    print("PLC not found on the network.")
    return None

# Function to get the operating mode of the PLC
def get_plc_operating_mode(ip):
    try:
        client = ModbusTcpClient(ip)
        client.connect()
        
        if not client.is_socket_open():
            print("Failed to connect to the PLC.")
            return None
        
        # Read the operating mode from the PLC (assuming it's stored in a specific register)
        # This register address may vary depending on the PLC model and vendor
        result = client.read_holding_registers(address=0x0000, count=1, unit=1)
        
        if result.isError():
            print("Error reading operating mode from the PLC.")
            return None
        
        mode = result.registers[0]
        
        # Map the mode value to a human-readable string
        mode_map = {
            0: "Stop",
            1: "Run",
            2: "Program",
            3: "Remote",
            4: "Reset",
            5: "Test/Monitor"
        }
        
        return mode_map.get(mode, "Unknown")
    
    except ConnectionException as e:
        print(f"Connection error: {e}")
        return None
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        operating_mode = get_plc_operating_mode(plc_ip)
        if operating_mode:
            print(f"PLC Operating Mode: {operating_mode}")
        else:
            print("Failed to retrieve the operating mode.")
    else:
        print("PLC not found. Please check the network configuration.")

if __name__ == "__main__":
    main()