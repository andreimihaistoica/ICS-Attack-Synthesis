import socket
from pycomm3 import LogixDriver

def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None
    finally:
        sock.close()

def change_operating_mode(plc_ip, mode):
    try:
        with LogixDriver(plc_ip) as plc:
            if mode == 'Program':
                plc.set_plc_mode('PROGRAM')
                print(f"PLC mode changed to {mode}")
            elif mode == 'Run':
                plc.set_plc_mode('RUN')
                print(f"PLC mode changed to {mode}")
            elif mode == 'Remote':
                plc.set_plc_mode('REMOTE')
                print(f"PLC mode changed to {mode}")
            elif mode == 'Stop':
                plc.set_plc_mode('STOP')
                print(f"PLC mode changed to {mode}")
            elif mode == 'Reset':
                plc.set_plc_mode('RESET')
                print(f"PLC mode changed to {mode}")
            elif mode == 'Test':
                plc.set_plc_mode('TEST')
                print(f"PLC mode changed to {mode}")
            else:
                print("Invalid mode")
    except Exception as e:
        print(f"Error changing PLC mode: {e}")

if __name0 == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        change_operating_mode(plc_ip, 'Program')