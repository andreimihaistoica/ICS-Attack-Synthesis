import socket
import pycomm

# Find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, 102))
            sock.close()
            return ip
        except socket.error:
            pass
    return None

# Collect point and tag values from the PLC
def collect_point_tag_values(plc_ip):
    # Create a PLC object
    plc = pycomm.S7_1200(plc_ip, 0, 1)

    # Read the point and tag values
    points = plc.read_area(pycomm.S7AreaDB, 1, 0, 10)
    tags = plc.read_area(pycomm.S7AreaDB, 2, 0, 10)

    # Print the point and tag values
    for i in range(len(points)):
        print(f"Point {i+1}: {points[i]}")
        print(f"Tag {i+1}: {tags[i]}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
        collect_point_tag_values(plc_ip)
    else:
        print("PLC not found")

if __name__ == "__main__":
    main()