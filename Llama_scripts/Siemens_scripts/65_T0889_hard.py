import scapy.all as scapy
import socket
import struct

# Define the PLC's IP address (will be discovered later)
plc_ip = None

# Define the PLC's port (e.g., Modbus TCP port 1700)
plc_port = 102

# Define the timeout for the ARP scan
arp_timeout = 2

# Define the program to modify
program_name = "FC1"  # Replace with the desired program name

# Define the new program code
new_program_code = """
// Block FC1 - Motor Temperature Control
// Converted from LAD to SCL

// Network 1 - Reset Fan B if temperature < 300
IF "Motor_Temp" < 300 THEN
    RESET("Activate_Fan_B");
END_IF;

// Network 2 - Control Fan indicator lights
IF "Activate_Fan_A" THEN
    "Fan_A_Red" := TRUE;
END_IF;

IF "Activate_Fan_B" THEN
    "Fan_B_Red" := TRUE;
END_IF;

// Network 3 - Activate Fan A if temperature is between 260 and 400
IF IN_RANGE(INT#260, "Motor_Temp", INT#400) THEN
    SET("Activate_Fan_A");
END_IF;

// Network 4 - Activate Fan B if temperature > 320
IF "Motor_Temp" > 320 THEN
    SET("Activate_Fan_B");
    SET("Master_Fan_B_HMI");
    SET("Activate_Fan_B");
END_IF;

// Network 5 - Control Fan A outputs
IF "Activate_Fan_A" THEN
    "Fan_A" := TRUE;
    "Fan_A_Green" := TRUE;
END_IF;

// Network 6 - Control Fan B outputs
IF "Activate_Fan_B" THEN
    "Fan_B" := TRUE;
    "Fan_B_Green" := TRUE;
END_IF;
"""

def discover_plc_ip():
    global plc_ip
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Replace with the subnet of your network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=arp_timeout, verbose=False)[0]
    for element in answered_list:
        if element[1].psrc == "192.168.1.100":  # Replace with the expected IP address of the PLC
            plc_ip = element[1].psrc
            break

def modify_program():
    global plc_ip
    if plc_ip is None:
        print("PLC IP address not found.")
        return

    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the PLC
    sock.connect((plc_ip, plc_port))

    # Send a request to the PLC to download the program
    download_request = b"\x03\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x03"

    # Send the request to the PLC
    sock.send(download_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Parse the response to extract the program code
    program_code_current = response[10:]

    # Modify the program code
    program_code_new = new_program_code.encode()

    # Send a request to the PLC to upload the modified program
    upload_request = b"\x03\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04"
    upload_request += program_code_new

    # Send the request to the PLC
    sock.send(upload_request)

    # Receive the response from the PLC
    response = sock.recv(1024)

    # Check if the program was uploaded successfully
    if response == b"\x03\x00\x00\x00\x00\x06\x01\x01\x00\x00\x00\x04":
        print("Program modified successfully")
    else:
        print("Error modifying program")

    # Close the socket
    sock.close()

if __name__ == "__main__":
    discover_plc_ip()
    modify_program()