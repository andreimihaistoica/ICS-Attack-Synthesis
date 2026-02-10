import snap7
from snap7.util import *
import socket

def discover_plc_ip():
    # Broadcast a message to discover the PLC's IP address
    # This is a simple example and may need to be adapted to your network
    broadcast_ip = "255.255.255.255"
    port = 102  # Default Siemens S7 port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for response

    try:
        sock.sendto(b"DiscoverPLC", (broadcast_ip, port))
        response, addr = sock.recvfrom(1024)
        return addr[0]  # Return the IP address of the PLC
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def change_plc_credentials(plc_ip):
    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # IP address, rack, slot

    # Change the PLC credentials (example: change the password)
    # This is a placeholder; actual implementation depends on the PLC's security model
    try:
        # Example: Write to a specific DB (Data Block) to change credentials
        db_number = 1  # Example DB number
        offset = 0  # Example offset
        new_password = b"NewPassword123"  # New password

        # Write the new password to the DB
        plc.db_write(db_number, offset, new_password)
        print(f"Credentials changed successfully on PLC at {plc_ip}.")
    except Exception as e:
        print(f"Failed to change credentials: {e}")
    finally:
        plc.disconnect()

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC discovery failed. Exiting.")
        return

    # Step 2: Change the PLC credentials
    change_plc_credentials(plc_ip)

if __name__ == "__main__":
    main()