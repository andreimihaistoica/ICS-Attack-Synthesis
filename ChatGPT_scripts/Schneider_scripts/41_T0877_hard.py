import sys
import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to scan the subnet for the PLC
def discover_plc(subnet, port=502):
    print("[*] Scanning the subnet for the PLC...")
    for i in range(1, 255):  # Increment through the subnet range
        ip_address = f"{subnet}.{i}"
        try:
            # Establish a basic socket connection to test if Modbus (port 502) is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Timeout set to 0.5 seconds
            sock.connect((ip_address, port))
            sock.close()
            print(f"[+] PLC Found at: {ip_address}")
            return ip_address
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("[-] No PLC Found in the subnet.")
    sys.exit(1)

# Function to collect the I/O Image using Modbus
def collect_io_image(ip_address):
    try:
        print(f"[*] Connecting to PLC at {ip_address}...")
        client = ModbusTcpClient(ip_address)
        if not client.connect():
            print("[-] Failed to connect to the PLC.")
            sys.exit(1)

        print("[*] Reading Input Image Table...")
        input_status = client.read_discrete_inputs(0, 10)  # Read first 10 input bits (%I0.0 - %I0.9)
        if input_status.isError():
            print("[-] Failed to read input status.")
        else:
            print("[+] Input Status:")
            print(input_status.bits)

        print("[*] Reading Output Image Table...")
        coil_status = client.read_coils(0, 10)  # Read first 10 output coils (%Q0.0 - %Q0.9)
        if coil_status.isError():
            print("[-] Failed to read output status.")
        else:
            print("[+] Output Status:")
            print(coil_status.bits)

        print("[*] Reading Memory Bits (%M)...")
        memory_status = client.read_coils(1000, 10)  # Read memory bits starting at address 1000 (%M1, etc.)
        if memory_status.isError():
            print("[-] Failed to read memory status.")
        else:
            print("[+] Memory Bits Status:")
            print(memory_status.bits)

        client.close()
        print("[*] Collection complete.")
    except ConnectionException as e:
        print(f"[-] Error connecting to the PLC: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Define subnet to scan (adjust as necessary)
    subnet = "192.168.9"
    
    # Step 1: Discover the PLC IP Address
    plc_ip = discover_plc(subnet)
    
    # Step 2: Collect the I/O Image
    collect_io_image(plc_ip)