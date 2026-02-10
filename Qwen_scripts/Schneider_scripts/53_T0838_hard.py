import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip.startswith('192.168.9.'):
                # Scan the subnet for the PLC
                for i in range(1, 255):
                    plc_ip = f"192.168.9.{i}"
                    client = ModbusTcpClient(plc_ip)
                    try:
                        # Try to connect to the PLC
                        if client.connect():
                            print(f"PLC found at IP: {plc_ip}")
                            client.close()
                            return plc_ip
                    except ConnectionException:
                        pass
                    finally:
                        client.close()
        except KeyError:
            continue
    return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    client = ModbusTcpClient(plc_ip)
    try:
        if client.connect():
            # Example: Disable a specific alarm by writing to a specific register
            # Assuming the alarm settings are stored in Modbus registers
            # For example, register 1000 might control the alarm settings
            # 0x0000 to disable the alarm, 0x0001 to enable the alarm
            client.write_register(1000, 0x0000)
            print("Alarm settings modified successfully.")
        else:
            print("Failed to connect to the PLC.")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()