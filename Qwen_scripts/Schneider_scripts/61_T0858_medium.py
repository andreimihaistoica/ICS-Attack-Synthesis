import socket
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple example using a broadcast to find the PLC
    # In a real-world scenario, you might use a more sophisticated method
    broadcast_ip = '255.255.255.255'
    port = 502  # Modbus TCP/IP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x00\x01\x00\x00\x00\x06\x01\x04\x00\x00\x00\x01'
    sock.sendto(message, (broadcast_ip, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to change the operating mode of the PLC
def change_operating_mode(plc_ip, mode):
    client = ModbusTcpClient(plc_ip)
    try:
        client.connect()
        if mode == 'Program':
            # Change to Program mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0001)
        elif mode == 'Run':
            # Change to Run mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0002)
        elif mode == 'Remote':
            # Change to Remote mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0003)
        elif mode == 'Stop':
            # Change to Stop mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0004)
        elif mode == 'Reset':
            # Change to Reset mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0005)
        elif mode == 'Test':
            # Change to Test mode (example register and value, adjust as needed)
            result = client.write_register(0x0000, 0x0006)
        else:
            print("Invalid mode")
            return

        if result.isError():
            print(f"Failed to change mode to {mode}")
        else:
            print(f"Successfully changed mode to {mode}")
    except ConnectionException:
        print("Failed to connect to the PLC")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        change_operating_mode(plc_ip, 'Program')

if __name__ == "__main__":
    main()