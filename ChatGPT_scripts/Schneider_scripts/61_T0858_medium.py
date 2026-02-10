import nmap
from pymodbus.client import ModbusTcpClient

# Function to scan the network and identify the PLC
def find_plc_ip(network_range):
    nm = nmap.PortScanner()
    print(f"Scanning network {network_range} for Modbus-compatible devices...")
    
    # Scan only for devices responding on port 502 (Modbus TCP)
    nm.scan(hosts=network_range, arguments='-p 502 --open')

    for host in nm.all_hosts():
        if 'tcp' in nm[host] and nm[host]['tcp'][502]['state'] == 'open':
            print(f"PLC Found at: {host}")
            return host
    return None

# Function to change the PLC mode via Modbus
def change_plc_mode(plc_ip, mode):
    modbus_client = ModbusTcpClient(plc_ip, port=502)
    
    try:
        if not modbus_client.connect():
            print("Failed to connect to PLC")
            return

        # Schneider Modicon PLCs typically use register 0x0800 (2048) for mode control.
        # Confirm with documentation or experiment with known Modicon devices.
        MODE_REGISTER = 0x0800  

        # Define mode codes based on Schneider PLC standards
        MODES = {
            "RUN": 0x01,
            "STOP": 0x02,
            "PROGRAM": 0x03,
            "RESET": 0x04
        }

        if mode not in MODES:
            print("Invalid mode! Choose from: RUN, STOP, PROGRAM, RESET")
            return
        
        print(f"Changing PLC mode to {mode}...")
        response = modbus_client.write_register(MODE_REGISTER, MODES[mode], unit=1)

        if response.isError():
            print("Failed to update PLC mode.")
        else:
            print(f"PLC mode successfully changed to {mode}.")

    finally:
        modbus_client.close()

# Main execution
if __name__ == "__main__":
    network_range = "192.168.1.0/24"  # Modify this based on your network configuration
    
    # Step 1: Find the PLC IP
    plc_ip = find_plc_ip(network_range)
    if plc_ip:
        # Step 2: Change the PLC mode (e.g., to PROGRAM mode)
        change_plc_mode(plc_ip, "PROGRAM")
    else:
        print("No PLC found on the network!")