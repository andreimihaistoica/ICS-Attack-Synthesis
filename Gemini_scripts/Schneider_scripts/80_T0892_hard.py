import snap7
import socket
import struct

# Configuration - Adjust as needed
PLC_IP = None  # Will be discovered if left as None
PLC_RACK = 0
PLC_SLOT = 1
MODBUS_ADDRESS = 1 # From the Serial Line (SL1) configuration
MODBUS_PASSWORD_REGISTER = 40001 # Example: Holding register for password.  **CRITICAL:  FIND THE CORRECT REGISTER**
NEW_PASSWORD = b'NewP@sswOrd123' # Example Password.  **CRITICAL:  USE A STRONG, SECURE PASSWORD**
MODBUS_SERIAL_PORT = "COM1" # Example Serial Port. **CRITICAL: CHECK YOUR DEVICE MANAGER FOR CORRECT PORT**
MODBUS_BAUD_RATE = 19200
MODBUS_PARITY = "E" # Even parity
MODBUS_DATA_BITS = 8
MODBUS_STOP_BITS = 1


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This is a VERY basic discovery and may not work in all network configurations.
    Requires nmap installed on the machine. Consider alternative discovery methods
    based on your network setup (e.g., reading a configuration file, querying a
    central device registry).

    Returns:
        str: The PLC's IP address, or None if not found.
    """
    try:
        import nmap  # Requires installing python-nmap
    except ImportError:
        print("nmap module not found. Install it using: pip install python-nmap")
        return None

    nm = nmap.PortScanner()
    # Scan the local network - this is a BROAD scan and can be noisy.  Adjust the target
    # range if you know a more specific subnet the PLC is likely on.
    nm.scan(hosts='192.168.9.0/24', arguments='-T4 -F') # Target local subnet, fast scan

    for host in nm.all_hosts():
        if 'mac' in nm[host]['addresses']:
            mac_address = nm[host]['addresses']['mac']
            # Schneider Electric PLCs often have MAC addresses starting with specific prefixes.
            #  This is NOT a guaranteed method but can help narrow down the search.
            if mac_address.startswith(('00:80:F4', '00:00:BC', '00:AE:C0')):  # Common Schneider Electric MAC prefixes
                print(f"Potential Schneider Electric PLC found at IP: {host} (MAC: {mac_address})")
                return host
    print("No Schneider Electric PLC found on the network (using nmap).")
    return None

def change_modbus_password_rtu(serial_port, baud_rate, parity, data_bits, stop_bits, modbus_address, register_address, new_password):
    """
    Changes the Modbus password by writing to a specified register over Modbus RTU.

    Args:
        serial_port (str): The serial port to use (e.g., "COM1").
        baud_rate (int): The baud rate.
        parity (str): Parity ("N", "E", or "O").
        data_bits (int): The number of data bits.
        stop_bits (int): The number of stop bits.
        modbus_address (int): The Modbus slave address.
        register_address (int): The register address to write to.
        new_password (bytes): The new password as a byte string.  Must be a valid length for the register.
    """
    try:
        import serial
        import modbus_tk
        import modbus_tk.defines as cst
        from modbus_tk import modbus_rtu

        # Create the Modbus RTU client
        master = modbus_rtu.RtuMaster(serial.Serial(port=serial_port, baudrate=baud_rate, bytesize=data_bits, parity=parity, stopbits=stop_bits, xonxoff=0))
        master.set_timeout(5.0)
        master.set_verbose(True)

        # Write the new password to the register
        try:
            # Convert password to a list of integers (Modbus expects integers for writing)
            password_data = [int(byte) for byte in new_password]
            master.write_multiple_registers(modbus_address, register_address, password_data) # Modified to write to the exact address
            print(f"Successfully changed password at register {register_address} (Modbus Addr: {modbus_address})")

        except modbus_tk.modbus.ModbusError as e:
            print(f"Modbus Error: {e}")

        finally:
            master.close()

    except ImportError as e:
        print(f"Missing dependencies: {e}.  Please install pyserial and modbus_tk.")
    except serial.SerialException as e:
        print(f"Serial communication error: {e}.  Check serial port and settings.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def main():
    global PLC_IP
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address not found.  Please manually set PLC_IP in the script.")
            return

    print(f"Using PLC IP address: {PLC_IP}")


    # Call the function to change the Modbus password over RTU.  
    #  **VERY IMPORTANT**:  Verify your serial settings, Modbus address, and register address.
    #  Writing to the wrong register CAN BRICK THE DEVICE.

    change_modbus_password_rtu(MODBUS_SERIAL_PORT, MODBUS_BAUD_RATE, MODBUS_PARITY, MODBUS_DATA_BITS, MODBUS_STOP_BITS,
                                MODBUS_ADDRESS, MODBUS_PASSWORD_REGISTER - 1, NEW_PASSWORD)  # Modbus register addressing is often 1-based.
    # You often need to subtract 1 to get the actual register address.




if __name__ == "__main__":
    main()