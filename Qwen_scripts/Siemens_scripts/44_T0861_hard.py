import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to read tags from the PLC
def read_tags(plc_ip, tags):
    with PLC() as plc:
        plc.open(plc_ip)
        if not plc.is_open:
            print(f"Failed to connect to PLC at {plc_ip}")
            return None

        tag_values = {}
        for tag in tags:
            try:
                value = plc.read(tag)
                tag_values[tag] = value
            except Exception as e:
                print(f"Failed to read tag {tag}: {e}")
                tag_values[tag] = None

        plc.close()
        return tag_values

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    print(f"PLC found at IP address: {plc_ip}")

    # List of tags to read
    tags = [
        "Fan_A", "Fan_B", "Fan_A_Red", "Fan_A_Green", "Fan_B_Red", "Fan_B_Green",
        "System_Byte", "FirstScan", "DiagStatusUpdate", "AlwaysTRUE", "AlwaysFALSE",
        "Clock_Byte", "Clock_10Hz", "Clock_5Hz", "Clock_2.5Hz", "Clock_2Hz",
        "Clock_1.25Hz", "Clock_1Hz", "Clock_0.625Hz", "Clock_0.5Hz", "Motor_Temp",
        "Activate_Fan_A", "Activate_Fan_B", "Master_Fan_B_HMI", "Motor_Status",
        "Master_OFF", "Tag_1", "Overheating_Check", "Tag_2", "Motor_Status_GET",
        "Tag_3", "Tag_4", "Tag_5"
    ]

    # Read the tags
    tag_values = read_tags(plc_ip, tags)

    # Print the tag values
    if tag_values:
        print("Tag Values:")
        for tag, value in tag_values.items():
            print(f"{tag}: {value}")

if __name__ == "__main__":
    main()