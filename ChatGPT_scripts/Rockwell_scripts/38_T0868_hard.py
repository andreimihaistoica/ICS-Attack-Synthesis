from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp
import time

# Function to find PLC on local network
def find_plc():
    target_ip_range = "192.168.1.0/24"  # Modify based on your network setup
    arp_request = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        if "Rockwell" in received.hwsrc:  # Filter by known MAC vendor if possible
            print(f"Potential PLC found at: {received.psrc}")
            return received.psrc  # Return the first detected PLC

    print("PLC not found on network.")
    return None

# Function to check operating mode via EtherNet/IP LogixDriver
def check_plc_mode(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            plc_info = plc.get_plc_info()
            print(f"Connected to PLC: {plc_info}")

            # Query a known status tag or register
            cpu_status = plc.read("ControllerStatus")

            if cpu_status:
                status_code = cpu_status.value
                print(f"Controller Status Code: {status_code}")

                mode = {
                    0: "Unknown",
                    1: "Program Mode",
                    2: "Run Mode",
                    3: "Test Mode",
                    4: "Remote Mode",
                    5: "Stop Mode"
                }.get(status_code, "Undefined Mode")

                print(f"PLC Operating Mode: {mode}")

            else:
                print("Failed to retrieve controller status.")

    except Exception as e:
        print(f"Error communicating with the PLC: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc()
    
    if plc_ip:
        check_plc_mode(plc_ip)
    else:
        print("Could not detect PLC IP. Ensure PLC is connected.")