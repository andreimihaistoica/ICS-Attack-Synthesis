from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver
import sys

def find_plc_ip():
    # Define the IP range to scan (adjust based on your network)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    plc_ip = None
    for sent, received in result:
        # Replace 'PLC_MAC_PREFIX' with the known prefix of the PLC's MAC address
        if received.src.startswith("PLC_MAC_PREFIX"):  # Example: "00:1D:9C"
            plc_ip = received.psrc
            print(f"PLC found at IP: {plc_ip}")
            break
    
    if not plc_ip:
        print("PLC not found in the network.")
        sys.exit(1)
    
    return plc_ip

def upload_plc_program(plc_ip):
    try:
        # Connect to the PLC using the found IP address
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")
            
            # Upload the program from the PLC
            program = plc.get_plc_info()
            print("PLC Program Information:")
            print(program)
            
            # Save the program logic to a file (optional)
            with open("plc_program.log", "w") as f:
                f.write(str(program))
            print("PLC program uploaded and saved to 'plc_program.log'")
    
    except Exception as e:
        print(f"Error uploading program from PLC: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    # Step 2: Upload the program from the PLC
    upload_plc_program(plc_ip)