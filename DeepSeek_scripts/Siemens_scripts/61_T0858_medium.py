import snap7
from snap7.util import *
from snap7.types import *
import socket

def find_plc_ip():
    """
    Discover the PLC's IP address on the network.
    This is a basic implementation and assumes the PLC responds to ARP requests.
    """
    # Replace with your network's subnet range
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC on port 102 (S7 communication port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 102))
            if result == 0:
                print(f"Found PLC at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            continue
    print("PLC not found on the network.")
    return None

def change_plc_mode(plc_ip, mode):
    """
    Change the operating mode of the Siemens S7-1200 PLC.
    Modes: 'STOP', 'RUN', 'RESET', etc.
    """
    try:
        # Connect to the PLC
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)
        
        # Get the current PLC status
        current_status = plc.get_cpu_state()
        print(f"Current PLC status: {current_status}")
        
        # Change the mode
        if mode == "STOP":
            plc.plc_stop()
            print("PLC changed to STOP mode.")
        elif mode == "RUN":
            plc.plc_run()
            print("PLC changed to RUN mode.")
        elif mode == "RESET":
            plc.plc_cold_start()
            print("PLC reset to COLD START.")
        else:
            print("Unsupported mode.")
        
        # Disconnect from the PLC
        plc.disconnect()
    except Exception as e:
        print(f"Error changing PLC mode: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        exit(1)
    
    # Step 2: Change the PLC's operating mode
    new_mode = "STOP"  # Change this to the desired mode: 'STOP', 'RUN', 'RESET', etc.
    change_plc_mode(plc_ip, new_mode)