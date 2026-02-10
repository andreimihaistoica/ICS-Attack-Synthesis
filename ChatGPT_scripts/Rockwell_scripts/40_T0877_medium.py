import socket
from pylogix import PLC

def discover_plc_ip():
    """
    Discovers the PLC's IP address by scanning the local network for active Rockwell PLC devices.
    It sends a UDP broadcast and listens for responses from a Rockwell PLC.
    """
    BROADCAST_IP = "255.255.255.255"  # Broadcast address
    DISCOVERY_PORT = 44818  # Ethernet/IP default port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3)  # Timeout for response

    # Sent discovery message specific to Rockwell devices
    discovery_message = bytes.fromhex("636F6E6E656374206D65646578")  # Sample broadcast message
    sock.sendto(discovery_message, (BROADCAST_IP, DISCOVERY_PORT))

    try:
        data, addr = sock.recvfrom(1024)  # Receive response
        print(f"PLC detected at: {addr[0]}")
        return addr[0]  # Extract PLC IP address
    except socket.timeout:
        print("No PLC response received.")
        return None
    finally:
        sock.close()

def read_io_image(plc_ip):
    """
    Reads Input and Output Image tables of a Rockwell Micro850 PLC.
    """
    if not plc_ip:
        print("PLC IP not found, exiting...")
        return
    
    with PLC() as comm:
        comm.IPAddress = plc_ip

        # Reading Input and Output tags (assuming they are named "InputImage" and "OutputImage")
        input_image_response = comm.Read("InputImage")
        output_image_response = comm.Read("OutputImage")

        if input_image_response.Status == "Success":
            print(f"Input Image Data: {input_image_response.Value}")
        else:
            print(f"Failed to read Input Image: {input_image_response.Status}")

        if output_image_response.Status == "Success":
            print(f"Output Image Data: {output_image_response.Value}")
        else:
            print(f"Failed to read Output Image: {output_image_response.Status}")

if __name__ == "__main__":
    plc_ip = discover_plc_ip()  # Discover PLC IP address dynamically
    read_io_image(plc_ip)  # Read the I/O image tables