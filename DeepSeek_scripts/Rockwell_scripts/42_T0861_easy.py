import snap7
import nmap
import sys

def discover_plc_ip():
    # Scan the network for devices with port 102 open (common for Siemens S7 PLCs)
    nm = nmap.PortScanner()
    nm.scan(hosts='192.168.1.0/24', arguments='-p 102 --open')

    plc_ip = None
    for host in nm.all_hosts():
        if nm[host].has_tcp(102) and nm[host]['tcp'][102]['state'] == 'open':
            plc_ip = host
            print(f"Discovered PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("No PLC found on the network.")
        sys.exit(1)

    return plc_ip

def collect_points_and_tags(plc_ip):
    # Connect to the PLC
    client = snap7.client.Client()
    try:
        client.connect(plc_ip, 0, 1)  # IP, rack, slot
        print(f"Connected to PLC at {plc_ip}")

        # Example: Read a specific memory area (e.g., DB1, start at byte 0, read 10 bytes)
        db_number = 1
        start_address = 0
        size = 10
        data = client.db_read(db_number, start_address, size)

        # Decode the data (example: interpret as integers)
        points = list(data)
        print(f"Collected points from DB{db_number}: {points}")

        # Example: Map points to tags (mock data)
        tags = {i: f"Tag_{i}" for i in range(len(points))}
        print("Mapped tags to points:")
        for point, tag in tags.items():
            print(f"Point {point}: {tag}")

    except Exception as e:
        print(f"Error communicating with PLC: {e}")
    finally:
        client.disconnect()

def main():
    # Step 1: Discover PLC IP
    plc_ip = discover_plc_ip()

    # Step 2: Collect points and tags
    collect_points_and_tags(plc_ip)

if __name__ == "__main__":
    main()