from snap7 import client
from scapy.all import ARP, Ether, srp
import time

def scan_network(ip_range):
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    result = srp(packet, timeout=3, verbose=0)[0]
    
    clients = []
    
    for sent, received in result:
        # for each response, append ip and mac address to `clients` list
        clients.append({'ip': received.psrc, 'ac': received.hwsrc})
    
    return clients

def upload_program(plc_ip, local_file_path):
    # Create a client object
    plc = client.Client()
    
    # Try to connect to the PLC
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return
    
    # Upload the program from the PLC to the local machine
    try:
        # The `upload` method is not directly available in snap7 for uploading programs.
        # Instead, you can read blocks from the PLC. The following example reads a DB (Data Block).
        # You need to adjust this based on the type of block and the specifics of your program.
        db_number = 1  # Replace with the number of the DB you want to read
        db_data = plc.read_area(0x84, db_number, 0, 100)  # Read 100 bytes from DB1
        
        # Save the data to a local file
        with open(local_file_path, 'wb') as file:
            file.write(db_data)
        
        print("Program uploaded successfully.")
    except Exception as e:
        print(f"Failed to upload program: {e}")
    finally:
        # Always disconnect when you're done
        plc.disconnect()

def find_plc_ip(clients):
    # This function assumes that the PLC has a specific MAC address or IP address range
    # Replace this with your actual logic to identify the PLC
    for client in clients:
        if client['ip'].startswith('192.168.1.100'):  # Replace with your PLC's IP address range
            return client['ip']
    return None

def main():
    ip_range = "192.168.1.0/24"
    local_file_path = "path/to/save/program.s7p"
    
    print("Scanning network for PLC...")
    clients = scan_network(ip_range)
    print("Available devices in the network:")
    print("IP" + " "*18+"MAC")
    for client in clients:
        print("{:16}    {}".format(client['ip'], client['mac']))
    
    plc_ip = find_plc_ip(clients)
    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")
        upload_program(plc_ip, local_file_path)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()