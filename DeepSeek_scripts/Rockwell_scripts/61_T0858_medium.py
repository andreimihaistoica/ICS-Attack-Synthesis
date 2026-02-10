from pycomm3 import LogixDriver, CIPDriver
import socket

def find_plc_ip():
    # Broadcast a message to discover the PLC on the network
    broadcast_ip = '255.255.255.255'
    port = 44818  # Default EtherNet/IP port
    message = b"Discover PLC"

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for responses

    # Send the broadcast message
    sock.sendto(message, (broadcast_ip, port))

    try:
        # Wait for a response
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC discovered at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No PLC found on the network.")
        return None
    finally:
        sock.close()

def change_plc_mode(plc_ip, mode='Program'):
    try:
        # Connect to the PLC using the discovered IP
        with LogixDriver(plc_ip) as plc:
            # Get the current mode
            current_mode = plc.get_plc_mode()
            print(f"Current PLC Mode: {current_mode}")

            # Change the PLC mode
            plc.set_plc_mode(mode)
            print(f"PLC mode changed to: {mode}")

            # Verify the new mode
            new_mode = plc.get_plc_mode()
            print(f"New PLC Mode: {new_mode}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Change the PLC's operating mode to 'Program'
        change_plc_mode(plc_ip, mode='Program')