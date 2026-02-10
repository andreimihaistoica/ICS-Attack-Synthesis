import socket
import struct
import time

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

# Function to detect the PLC's operating mode
def detect_operating_mode():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)

        # Create a Modbus TCP packet to read the PLC's operating mode
        packet = bytearray()
        packet.append(0x00)  # Transaction ID
        packet.append(0x00)
        packet.append(0x00)  # Protocol ID
        packet.append(0x00)
        packet.append(0x00)  # Length
        packet.append(0x06)
        packet.append(0x01)  # Unit ID
        packet.append(0x03)  # Function code for reading operating mode
        packet.append(0x00)  # Starting address
        packet.append(0x00)
        packet.append(0x00)  # Quantity of registers
        packet.append(0x01)

        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout to avoid waiting indefinitely
        sock.settimeout(1)

        # Try to connect to the PLC
        try:
            sock.connect((plc_ip, 1700))
            print("Connected to the PLC")

            # Send the packet to read the PLC's operating mode
            sock.sendall(packet)

            # Receive the response from the PLC
            response = sock.recv(1024)
            print("Received response:", response)

            # Parse the response to extract the operating mode information
            # This step is highly dependent on the specific protocol and device
            operating_mode = response[9:]  # Remove the header
            print("Operating mode:", operating_mode)

            # Determine the PLC's operating mode based on the response
            if operating_mode == b'\x01':
                print("PLC is in Program mode")
            elif operating_mode == b'\x02':
                print("PLC is in Run mode")
            elif operating_mode == b'\x03':
                print("PLC is in Remote mode")
            elif operating_mode == b'\x04':
                print("PLC is in Stop mode")
            elif operating_mode == b'\x05':
                print("PLC is in Reset mode")
            elif operating_mode == b'\x06':
                print("PLC is in Test/Monitor mode")
            else:
                print("Unknown operating mode")
        except socket.error as e:
            print("Failed to connect to the PLC:", str(e))
        finally:
            # Close the socket
            sock.close()
    else:
        print("PLC IP address not found")

# Main function to start the detection of the PLC's operating mode
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        detect_operating_mode()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()