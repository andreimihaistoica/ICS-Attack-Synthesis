from pymodbus.client import ModbusTcpClient
import scapy.all as scapy
import time

# Function to find the IP address of the PLC using ARP requests
def find_plc_ip(subnet="192.168.1.0/24"):
    print("[*] Scanning for PLC in subnet:", subnet)
    
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        if "Siemens" in received.psrc or "Rockwell" in received.psrc:  # Adjust vendor detection
            print("[+] Found PLC at:", received.psrc)
            return received.psrc
    
    print("[-] No PLC found in the subnet.")
    return None

# Function to restart the PLC using Modbus (Modify for other protocols as needed)
def restart_plc(plc_ip):
    print(f"[*] Attempting to restart PLC at {plc_ip}...")
    
    try:
        client = ModbusTcpClient(plc_ip, port=502)
        client.connect()
        
        # Modbus function code 5 (Write Single Coil) - Example Restart Command
        restart_register = 0x0000  # Change based on PLC-specific restart/shutdown coil address
        response = client.write_coil(restart_register, True)
        
        if response.isError():
            print("[-] Restart command failed.")
        else:
            print("[+] Restart command sent successfully.")
        
        client.close()
    except Exception as e:
        print(f"[ERROR] Could not restart PLC: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Discover PLC's IP
    if plc_ip:
        restart_plc(plc_ip)  # Restart the PLC