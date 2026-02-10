import snap7
import socket
import struct
import nmap

def find_plc_ip():
    """
    Scans the local network for Siemens PLCs and returns the first found IP address.
    """
    nm = nmap.PortScanner()
    print("[*] Scanning network for Siemens PLCs...")
    
    # Adjust the subnet accordingly
    subnet = '192.168.1.0/24'
    
    # Scan for devices with the S7 port (102) open
    nm.scan(hosts=subnet, arguments="-p 102 --open")
    
    for host in nm.all_hosts():
        print(f"[+] Potential PLC found: {host}")
        return host  # Return the first found PLC
    
    print("[-] No PLCs found.")
    return None

def read_plc_io_image(plc_ip):
    """
    Connects to the PLC and retrieves the I/O Image (Process Image Input and Output tables).
    """
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200/1500 PLCs

        if not client.get_connected():
            print("[-] Failed to connect to the PLC.")
            return
        
        print("[*] Connected to PLC at", plc_ip)

        # Read Process Input Image (default DB 124 for Siemens PLCs)
        input_image = client.read_area(snap7.types.Areas.PE, 0, 0, 256)
        print("[*] Process Input Image Data (First 256 Bytes):", input_image.hex())

        # Read Process Output Image (default DB 125 for Siemens PLCs)
        output_image = client.read_area(snap7.types.Areas.PA, 0, 0, 256)
        print("[*] Process Output Image Data (First 256 Bytes):", output_image.hex())

        client.disconnect()
        print("[+] Disconnected from PLC.")
    
    except Exception as e:
        print("[-] Error accessing PLC:", e)

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        read_plc_io_image(plc_ip)
    else:
        print("[-] No PLC IP found, exiting.")