from scapy.all import *
import scapy.layers.inet as inet
import subprocess
import time

# Configuration
PLC_PORT = 502  # Default Modbus TCP Port
BROADCAST_IP = "255.255.255.255"
NETWORK_INTERFACE = "Ethernet"  # Change this according to your system

def find_plc_ip():
    """Scans the network to identify the PLC based on Modbus behavior."""
    print("[*] Scanning network for PLC...")
    
    responses, _ = sr(IP(dst="255.255.255.255")/TCP(dport=PLC_PORT, flags="S"), timeout=5, verbose=False)
    
    for sent, received in responses:
        if received.haslayer(TCP) and received[TCP].sport == PLC_PORT:
            print(f"[+] PLC Identified at {received[IP].src}")
            return received[IP].src
    
    print("[-] No PLC found on the network.")
    return None

def block_command_messages(plc_ip):
    """Implements firewall rule to block command messages to the identified PLC."""
    print(f"[*] Blocking command messages to the PLC at {plc_ip}...")

    try:
        # Using Windows netsh firewall to block traffic to PLC on Modbus TCP port
        command = f'netsh advfirewall firewall add rule name="Block PLC Commands" dir=out action=block remoteip={plc_ip} protocol=TCP remoteport={PLC_PORT}'
        subprocess.run(command, shell=True, check=True)
        print("[+] Successfully blocked command messages to PLC.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Firewall rule failed: {e}")

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        block_command_messages(plc_ip)

if __name__ == "__main__":
    main()