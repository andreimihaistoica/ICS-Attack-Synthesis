import socket
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the engineering workstation
    subnet = "192.168.9.0/24"
    plc_ip = None

    # Scan the subnet for the PLC
    for i in range(1, 255):
        ip = f"192.168.9.{i}"
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                plc_ip = ip
                client.close()
                break
        except ConnectionException:
            continue

    return plc_ip

# Function to block the command message
def block_command_message(plc_ip):
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    try:
        # Simulate blocking the command message by not writing to the PLC
        # For example, the command to activate the fan is typically written to %Q0.0
        # Here, we will intercept and discard the command
        print("Blocking command message to the PLC...")

        # Normally, you would write to the PLC to activate the fan
        # client.write_coil(0, True)  # This would activate the fan

        # Instead, we do nothing, effectively blocking the command
        print("Command message blocked.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        block_command_message(plc_ip)
    else:
        print("PLC not found on the network.")