import socket
import ipaddress
import time
from pymodbus.client import ModbusTcpClient

# Configuration (CHANGE THESE!)
PLC_IP_ADDRESS = None # will attempt to discover if None
PLC_PORT = 502  # Standard Modbus port
PROGRAM_MODE_REGISTER = 40001  # Example register (PLC-SPECIFIC!)
PROGRAM_MODE_VALUE = 1  # Example value to set "Program" mode
STOP_MODE_REGISTER = 40002 # Example register for stop mode
STOP_MODE_VALUE = 2 #Example Value for stop mode.
READ_MODE_REGISTER = 40003 #Example register to read current mode.

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This is a VERY basic approach.  Consider more sophisticated methods.
    """
    try:
        # Get the local machine's IP address and network prefix
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = ipaddress.ip_network(local_ip + '/24', strict=False) # Assuming /24 subnet

        print(f"Scanning network: {network}")

        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str == local_ip:
                continue # Skip the local machine

            # Simple ping (can be unreliable)
            try:
                socket.inet_aton(ip_str) # Validate IP
                #Attempt a connection to port 502 to see if it works
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1) # Short timeout
                result = s.connect_ex((ip_str, PLC_PORT))
                if result == 0:
                    print(f"Potential PLC found at: {ip_str}")
                    return ip_str
                s.close()


            except socket.error as e:
                pass  # Invalid IP or other socket error
            except Exception as e:
                print(f"Error during discovery: {e}")

        print("PLC IP address not automatically found.")
        return None

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None

def change_plc_mode(plc_ip, program_mode_register, program_mode_value,stop_mode_register, stop_mode_value):
    """
    Attempts to change the PLC's operating mode using Modbus TCP.
    """
    try:
        client = ModbusTcpClient(plc_ip, port=PLC_PORT)

        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}:{PLC_PORT}")
            return False

        # Attempt to change to Program mode

        print(f"Attempting to set PLC to Program mode (register {program_mode_register} to value {program_mode_value}).")
        result = client.write_register(program_mode_register, program_mode_value)

        if result.isError():
            print(f"Error writing to register {program_mode_register}: {result}")
            print("Attempting to set PLC to Stop mode")
            result = client.write_register(stop_mode_register, stop_mode_value)
            if result.isError():
                print(f"Error writing to register {stop_mode_register}: {result}")
                return False

        #Give time for PLC to switch modes
        time.sleep(2)

        #Verify the mode change
        read_result = client.read_holding_registers(READ_MODE_REGISTER, 1)
        if read_result.isError():
            print(f"Error reading register {READ_MODE_REGISTER}: {read_result}")
            client.close()
            return False
        else:
            current_mode = read_result.registers[0]
            print(f"PLC mode changed to {current_mode}.")


        client.close()
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False


if __name__ == "__main__":
    if PLC_IP_ADDRESS is None:
        PLC_IP_ADDRESS = discover_plc_ip()

    if PLC_IP_ADDRESS:
        print(f"Using PLC IP address: {PLC_IP_ADDRESS}")
        if change_plc_mode(PLC_IP_ADDRESS, PROGRAM_MODE_REGISTER, PROGRAM_MODE_VALUE,STOP_MODE_REGISTER,STOP_MODE_VALUE):
            print("Successfully (attempted to) change PLC mode.")
        else:
            print("Failed to change PLC mode.")
    else:
        print("Could not determine PLC IP address.  Please configure PLC_IP_ADDRESS manually.")