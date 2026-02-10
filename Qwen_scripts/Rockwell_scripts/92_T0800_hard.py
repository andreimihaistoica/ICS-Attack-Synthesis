import socket
import pycomm3
from pycomm3 import LogixDriver

def discover_plc_ip():
    # This function uses a simple UDP broadcast to discover the PLC's IP address
    # Note: This is a simplified example and may need to be adapted for your network setup
    broadcast_ip = '255.255.255.255'
    port = 44818  # Common port for Rockwell PLCs

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', port))

    # Send a broadcast message to discover the PLC
    sock.sendto(b'DISCOVER', (broadcast_ip, port))

    # Receive the response
    data, addr = sock.recvfrom(1024)
    sock.close()

    return addr[0]

def activate_firmware_update_mode(plc_ip):
    with LogixDriver(plc_ip) as plc:
        # Activate firmware update mode
        plc.write('FirmwareUpdateMode', True)
        print(f"Firmware update mode activated on {plc_ip}")

def deactivate_firmware_update_mode(plc_ip):
    with LogixDriver(plc_ip) as plc:
        # Deactivate firmware update mode
        plc.write('FirmwareUpdateMode', False)
        print(f"Firmware update mode deactivated on {plc_ip}")

def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    print(f"Discovered PLC IP: {plc_ip}")

    # Activate firmware update mode
    activate_firmware_update_mode(plc_ip)

    # Deactivate firmware update mode
    deactivate_firmware_update_mode(plc_ip)

if __name__ == "__main__":
    main()