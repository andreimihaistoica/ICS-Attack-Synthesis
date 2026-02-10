import sys
import time
from scapy.all import ARP, Ether, srp
import snap7

def find_plc_ip(target_ip_range):
    """
    Finds the IP address of the Siemens S7-1200 PLC using an ARP scan over the given IP address range.
    """
    print("[*] Scanning for devices in the network...")
    arp = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=3, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    print("[*] Found devices on the network:")
    for device in devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}")
    
    # Assuming the PLC's MAC address is known or filtering logic is provided elsewhere
    # Here, we'll return the first found device. Modify this logic as needed.
    if devices:
        return devices[0]['ip']
    else:
        print("[!] No devices found.")
        sys.exit(1)

def restart_plc(plc_ip):
    """
    Connects to the Siemens S7-1200 PLC at the given IP address and restarts it.
    """
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (default for S7-1200)
        
        if plc.get_connected():
            print("[*] Connected to PLC. Issuing stop command...")
            plc.plc_stop()  # Stop command
            
            print("[*] Waiting for 5 seconds before restarting...")
            time.sleep(5)
            
            print("[*] Issuing start command...")
            plc.plc_start()  # Start command
            
            print("[*] PLC restart successfully executed.")
        else:
            print("[!] Could not connect to the PLC.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        plc.disconnect()
        plc.destroy()

if __name__ == "__main__":
    # Specify the target IP range for finding the PLC
    target_ip_range = "192.168.0.0/24"  # Adjust this to match your network range

    print("[*] Starting script...")
    plc_ip = find_plc_ip(target_ip_range)
    print(f"[*] PLC IP address found: {plc_ip}")
    
    restart_plc(plc_ip)