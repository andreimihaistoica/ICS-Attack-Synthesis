import socket
import netifaces as ni
from pyModbusTCP.client import ModbusClient

# Function to find the PLC's IP address on the network
def find_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # Check if the IP is in the local network (192.168.x.x or 10.x.x.x)
            if ip.startswith('192.168.') or ip.startswith('10.'):
                # Create a socket to send a broadcast message
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind((ip, 0))
                sock.settimeout(2)
                
                # Send a broadcast message to discover the PLC
                sock.sendto(b'PLC_DISCOVERY', ('255.255.255.255', 502))
                
                # Receive the response
                data, addr = sock.recvfrom(1024)
                if data == b'PLC_RESPONSE':
                    return addr[0]
        except Exception as e:
            print(f"Error on interface {interface}: {e}")
    
    return None

# Function to get the operating mode of the PLC
def get_plc_operating_mode(plc_ip):
    # Create a Modbus client
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)
    
    if not client.is_open():
        if not client.open():
            print(f"Unable to connect to PLC at {plc_ip}")
            return None
    
    # Read the operating mode from the PLC
    # Assuming the operating mode is stored in a specific register (e.g., register 0)
    result = client.read_holding_registers(0, 1)
    
    if result:
        mode = result[0]
        modes = {
            0: 'Program',
            1: 'Run',
            2: 'Remote',
            3: 'Stop',
            4: 'Reset',
            5: 'Test/Monitor'
        }
        return modes.get(mode, 'Unknown')
    else:
        print("Failed to read operating mode from PLC")
        return None

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Get the operating mode
        operating_mode = get_plc_operating_mode(plc_ip)
        if operating_mode:
            print(f"PLC Operating Mode: {operating_mode}")
        else:
            print("Failed to determine the operating mode of the PLC")
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()