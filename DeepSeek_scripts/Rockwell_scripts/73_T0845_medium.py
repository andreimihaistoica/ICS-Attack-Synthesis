import os
import subprocess
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Broadcast a UDP message to discover the PLC
    broadcast_ip = "255.255.255.255"
    port = 44818  # Common port for Rockwell PLCs
    message = b"DiscoverPLC"  # Custom discovery message

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Timeout for discovery

    try:
        # Send the discovery message
        sock.sendto(message, (broadcast_ip, port))
        print("Broadcasting discovery message...")

        # Wait for a response from the PLC
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if data.startswith(b"PLCResponse"):
                    plc_ip = addr[0]
                    print(f"PLC Discovered at IP: {plc_ip}")
                    return plc_ip
            except socket.timeout:
                print("PLC discovery timed out. No response received.")
                return None
    finally:
        sock.close()

# Function to upload the program from the PLC
def upload_program(plc_ip):
    # Path to the Rockwell software executable (e.g., CCW or Studio 5000)
    software_path = r"C:\Program Files (x86)\Rockwell Software\CCW\CCW.exe"
    
    # Command to upload the program from the PLC
    upload_command = [
        software_path,
        "--upload",
        f"--ip={plc_ip}",
        "--output=uploaded_program.acd"  # Output file for the uploaded program
    ]

    try:
        # Execute the command
        print(f"Uploading program from PLC at {plc_ip}...")
        subprocess.run(upload_command, check=True)
        print("Program uploaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading program: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Step 2: Upload the program from the PLC
        upload_program(plc_ip)
    else:
        print("PLC IP address not found. Exiting script.")