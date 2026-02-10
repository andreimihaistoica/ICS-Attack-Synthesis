from snap7 import client
import socket
import struct

def find_plc_ip():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 0))
    sock.settimeout(1)

    # Send a broadcast message to the network
    message = b"Hello, PLC!"
    sock.sendto(message, ("255.255.255.255", 102))

    # Listen for responses
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        return None

def change_credential(plc_ip, new_credential):
    # Create a client object
    plc = client.Client()
    
    # Try to connect to the PLC
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return
    
    # Change the credential
    try:
        # Replace the following line with the actual address of the credential
        credential_address = 0x8200  # Example address
        new_credential_bytes = new_credential.encode()
        plc.write_area(0x84, 1, credential_address, new_credential_bytes)  # Write the new credential
        
        print("Credential changed successfully.")
    except Exception as e:
        print(f"Failed to change credential: {e}")
    finally:
        # Always disconnect when you're done
        plc.disconnect()

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")
        
        # Change the credential
        new_credential = "new_password"
        change_credential(plc_ip, new_credential)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()