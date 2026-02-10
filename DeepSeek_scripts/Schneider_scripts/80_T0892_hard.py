from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import socket

# Function to discover the PLC's IP address
def discover_plc_ip(subnet="192.168.9.0/24"):
    from ipaddress import ip_network
    import subprocess

    for ip in ip_network(subnet).hosts():
        ip = str(ip)
        try:
            # Ping the IP to check if it's reachable
            subprocess.check_output(["ping", "-n", "1", "-w", "1000", ip], stderr=subprocess.STDOUT)
            # Attempt to connect to Modbus TCP port (502)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((ip, 502))
                if result == 0:
                    return ip
        except subprocess.CalledProcessError:
            pass
    return None

# Function to change the PLC's credentials
def change_plc_credentials(ip_address, new_password):
    try:
        # Connect to the PLC using Modbus TCP
        client = ModbusTcpClient(ip_address)
        client.connect()

        # Example: Write a new password to a specific register (adjust as needed)
        # This is a hypothetical example; real implementation depends on the PLC's Modbus map
        address = 0x1000  # Hypothetical register for password storage
        value = int.from_bytes(new_password.encode(), 'big')  # Convert password to integer
        client.write_register(address, value)

        print(f"Credentials changed successfully on PLC at {ip_address}.")
    except ModbusException as e:
        print(f"Failed to change credentials on PLC: {e}")
    finally:
        client.close()

# Main script
if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("Could not discover the PLC's IP address.")
        exit(1)

    print(f"Discovered PLC at IP: {plc_ip}")

    # Define the new password
    new_password = "NewSecurePassword123"

    # Change the PLC's credentials
    change_plc_credentials(plc_ip, new_password)