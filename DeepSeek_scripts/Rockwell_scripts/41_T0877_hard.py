from pycomm3 import LogixDriver
import socket

def find_plc_ip():
    # Broadcast a message to find the PLC's IP address
    # This is a simplified example and may need to be adapted based on your network setup
    broadcast_ip = "255.255.255.255"
    port = 44818  # Common port for Allen-Bradley PLCs

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)  # Timeout for receiving responses

    try:
        sock.sendto(b"WhoIs", (broadcast_ip, port))
        data, addr = sock.recvfrom(1024)
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
            # Read the I/O Image (Input and Output tables)
            input_table = plc.read('I:0')
            output_table = plc.read('O:0')

            print("Input Image Table:")
            print(input_table)
            print("\nOutput Image Table:")
            print(output_table)

            return input_table, output_table
    except Exception as e:
        print(f"Error collecting I/O Image: {e}")
        return None, None

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Collect the I/O Image
        input_table, output_table = collect_io_image(plc_ip)

        if input_table and output_table:
            print("I/O Image collection successful.")
        else:
            print("Failed to collect I/O Image.")
    else:
        print("PLC IP address not found.")