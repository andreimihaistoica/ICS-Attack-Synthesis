from pycomm3 import LogixDriver
import socket
import sys

def discover_plc_ip():
    # Broadcast a message to discover the PLC on the network
    broadcast_ip = '255.255.255.255'
    port = 44818  # Common port for Rockwell PLCs

    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)  # Set a timeout for the broadcast

        # Send a broadcast message
        sock.sendto(b'DISCOVER_PLC', (broadcast_ip, port))

        # Receive the response
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Discovered PLC at IP: {plc_ip}")
        return plc_ip

    except Exception as e:
        print(f"Error discovering PLC: {e}")
        return None

    finally:
        sock.close()

def change_plc_credentials(plc_ip, new_password):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Change the password (example: using a hypothetical method)
            plc.write_tag('Security.Password', new_password)
            print(f"Successfully changed PLC credentials. New password: {new_password}")

    except Exception as e:
        print(f"Error changing PLC credentials: {e}")

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if not plc_ip:
        print("Could not discover PLC on the network.")
        sys.exit(1)

    # Step 2: Change the PLC credentials
    new_password = "NewSecurePassword123"  # Define the new password
    change_plc_credentials(plc_ip, new_password)