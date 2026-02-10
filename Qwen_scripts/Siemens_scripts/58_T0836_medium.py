import socket
import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet and range to scan
    subnet = "192.168.1."
    start_ip = 1
    end_ip = 254

    for i in range(start_ip, end_ip + 1):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.S7Client() as client:
                client.connect(ip, 0, 1)
                if client.is_connected():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Failed to connect to {ip}: {e}")
    return None

# Function to modify a parameter in the PLC
def modify_plc_parameter(plc_ip, parameter_name, new_value):
    try:
        with pycomm3.S7Client() as client:
            client.connect(plc_ip, 0, 1)
            if client.is_connected():
                # Example: Modify a parameter (assuming it's an integer)
                client.write_area(pycomm3.s7.S7AreaDB, 1, 0, [new_value])
                print(f"Parameter {parameter_name} modified to {new_value}")
            else:
                print("Failed to connect to the PLC")
    except Exception as e:
        print(f"Error modifying parameter: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Define the parameter to modify and the new value
        parameter_name = "MotorRunTime"
        new_value = 120  # Example: Change the motor run time to 120 seconds

        # Modify the parameter
        modify_plc_parameter(plc_ip, parameter_name, new_value)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()