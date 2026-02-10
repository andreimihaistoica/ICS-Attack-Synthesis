from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp

def find_plc_ip(network_range="192.168.1.0/24"):
    """Scan the network to find the PLC's IP address via ARP Request."""
    print("[+] Scanning the network to find PLC IP...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range), timeout=2, verbose=False)

    for _, recv in ans:
        ip = recv.psrc
        mac = recv.hwsrc
        print(f"[*] Found Device: IP={ip}, MAC={mac}")
        # Assuming we recognize the PLC MAC address pattern or IP range
        if mac.startswith("00:0e") or mac.startswith("00:1a"):  # Example MAC prefixes for PLC vendors
            print(f"[+] Identified PLC at IP: {ip}")
            return ip

    print("[-] No PLC found in the network.")
    return None

def collect_io_image(plc_ip):
    """Connects to PLC and reads I/O Image state."""
    try:
        with LogixDriver(plc_ip) as plc:
            print("[+] Connected to PLC. Reading I/O Image...")

            # Example I/O Image Tags (Change according to PLC memory layout)
            input_table = plc.read("Local:1:I.Data")   # Example: Digital Input Table
            output_table = plc.read("Local:2:O.Data")  # Example: Digital Output Table

            print("[*] Input Table: ", input_table)
            print("[*] Output Table:", output_table)

            # Save data for further analysis
            with open("plc_io_image_log.txt", "w") as log_file:
                log_file.write(f"PLC IP: {plc_ip}\n")
                log_file.write(f"Input Image: {input_table}\n")
                log_file.write(f"Output Image: {output_table}\n")

            print("[+] I/O Image collected and saved.")
    except Exception as e:
        print(f"[-] Error in collecting I/O Image: {e}")

def main():
    plc_ip = find_plc_ip()
    
    if plc_ip:
        collect_io_image(plc_ip)
    else:
        print("[-] No PLC detected. Exiting...")

if __name__ == "__main__":
    main()