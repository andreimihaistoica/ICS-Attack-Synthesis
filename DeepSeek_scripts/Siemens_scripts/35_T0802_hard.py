import snap7
import socket
from snap7.util import *
from snap7.types import *
import struct

# Function to discover PLC IP address using a simple network scan
def discover_plc_ip():
    for i in range(1, 255):
        ip = f"192.168.0.{i}"
        try:
            # Try to connect to the PLC on port 102 (S7 protocol)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 102))
            if result == 0:
                print(f"PLC found at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    return None

# Function to collect data from the PLC
def collect_data(plc_ip):
    try:
        # Initialize the PLC client
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)

        # Collect tags and memory areas
        print("Collecting PLC tags and memory areas...")
        # Read Motor_Temp (Int %MW7)
        motor_temp = plc.read_area(Areas.MK, 0, 7, S7WLWord)
        motor_temp_value = get_int(motor_temp, 0)
        print(f"Motor_Temp: {motor_temp_value}")

        # Read Fan_A (Bool %Q0.0)
        fan_a = plc.read_area(Areas.PA, 0, 0, S7WLBit)
        fan_a_value = get_bool(fan_a, 0, 0)
        print(f"Fan_A: {fan_a_value}")

        # Read Fan_B (Bool %Q0.1)
        fan_b = plc.read_area(Areas.PA, 0, 1, S7WLBit)
        fan_b_value = get_bool(fan_b, 0, 1)
        print(f"Fan_B: {fan_b_value}")

        # Read System_Byte (Byte %MB5)
        system_byte = plc.read_area(Areas.MK, 0, 5, S7WLByte)
        system_byte_value = get_byte(system_byte, 0)
        print(f"System_Byte: {system_byte_value}")

        # Read Clock_Byte (Byte %MB6)
        clock_byte = plc.read_area(Areas.MK, 0, 6, S7WLByte)
        clock_byte_value = get_byte(clock_byte, 0)
        print(f"Clock_Byte: {clock_byte_value}")

        # Disconnect from the PLC
        plc.disconnect()
        print("Data collection completed.")

    except Exception as e:
        print(f"Error collecting data from PLC: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Discover PLC IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found on the network.")
        exit(1)

    # Step 2: Collect data from the PLC
    collect_data(plc_ip)