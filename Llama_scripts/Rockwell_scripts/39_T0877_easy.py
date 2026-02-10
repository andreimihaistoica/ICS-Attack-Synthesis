import snap7
import socket

def get_plc_ip():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set the broadcast address and port
    broadcast_address = '192.168.0.255'  # Replace with your broadcast address
    broadcast_port = 102

    # Create a broadcast message
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Send the broadcast message
    sock.sendto(message, (broadcast_address, broadcast_port))

    # Receive the response
    sock.settimeout(1)
    try:
        response, address = sock.recvfrom(1024)
        plc_ip = address[0]
        return plc_ip
    except socket.timeout:
        print("No PLC found")
        return None

def capture_io_image(plc_ip):
    try:
        # Create a client object
        client = snap7.S7Client()

        # Connect to the PLC
        client.ConnectTo(plc_ip, 0, 1)  # Rack 0, Slot 1

        # Get the I/O image
        input_image = client.ReadArea(snap7.S7AreaPE, 0, 0, 64)  # Read 64 bytes from the input image
        output_image = client.ReadArea(snap7.S7AreaPA, 0, 0, 64)  # Read 64 bytes from the output image

        # Print the I/O image
        print("Input Image:")
        for i in range(len(input_image)):
            print(f"Byte {i}: {input_image[i]}")

        print("Output Image:")
        for i in range(len(output_image)):
            print(f"Byte {i}: {output_image[i]}")

        # Disconnect from the PLC
        client.Disconnect()

    except Exception as e:
        print(f"Error: {e}")

# Get the PLC's IP address
plc_ip = get_plc_ip()

if plc_ip:
    # Capture the I/O image
    capture_io_image(plc_ip)