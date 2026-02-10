import socket
from pycomm3 import LogixDriver

def find_plc_ip():
    # Example: Broadcast to find the PLC's IP address
    # This is a simplified example; in practice, you may need to use a more robust method.
    broadcast_ip = '255.255.255.255'
    port = 44818  # Default port for Modbus TCP

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)

    try:
        sock.sendto(b'discovery_packet', (broadcast_ip, port))
        response, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def collect_io_image(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Read the input image table
            input_image = plc.read('I')

            # Read the output image table
            output_image = plc.read('O')

            # Print the collected I/O Image data
            print("Input Image Table:")
            print(input_image)

            print("\nOutput Image Table:")
            print(output_image)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Collect the I/O Image state
        collect_io_image(plc_ip)