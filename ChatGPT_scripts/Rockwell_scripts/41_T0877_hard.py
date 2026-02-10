from pylogix import PLC
import socket
import struct

def find_plc_ip():
    """
    Scan the network for an EtherNet/IP device (Rockwell PLC).
    This function sends a broadcast and listens for a response.
    """
    BROADCAST_IP = "255.255.255.255"
    UDP_PORT = 44818  # EtherNet/IP default port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    # Send Rockwell discovery packet
    discovery_packet = bytes.fromhex('63 00 00 00 00 00 00 00')
    sock.sendto(discovery_packet, (BROADCAST_IP, UDP_PORT))

    try:
        data, addr = sock.recvfrom(1024)  # Receive response
        plc_ip = addr[0]
        print(f"Discovered PLC IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No response received, check network connection.")
        return None
    finally:
        sock.close()


def collect_io_image(plc_ip):
    """
    Connect to the Micro850 PLC and read the I/O image table.
    """
    if not plc_ip:
        print("PLC IP not found. Exiting.")
        return

    plc = PLC()
    plc.IPAddress = plc_ip

    # Identified I/O Image tags in structured text
    io_tags = [
        "_IO_EM_DI_00", "_IO_EM_DI_01", "_IO_EM_DI_02",  # Example digital inputs
        "_IO_EM_DO_02", "_IO_EM_DO_06", "_IO_EM_DO_07"   # Example digital outputs controlling fan and LEDs
    ]

    io_state = {}

    for tag in io_tags:
        try:
            response = plc.Read(tag)
            if response.Status == 'Success':
                io_state[tag] = response.Value
                print(f"Collected {tag}: {response.Value}")
            else:
                print(f"Failed to read {tag}: {response.Status}")
        except Exception as e:
            print(f"Error reading {tag}: {e}")

    plc.Close()

    # Write collected data to file for further analysis
    with open("io_image_log.txt", "w") as file:
        for k, v in io_state.items():
            file.write(f"{k}: {v}\n")


if __name__ == "__main__":
    plc_ip = find_plc_ip()
    collect_io_image(plc_ip)