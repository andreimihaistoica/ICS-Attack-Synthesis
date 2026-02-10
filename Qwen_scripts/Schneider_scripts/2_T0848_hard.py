import socket
import struct
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

# Function to find the PLC's IP address
def find_plc_ip(target_ip_range):
    # Create an ARP request packet
    arp = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and get the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter the devices to find the PLC
    for device in devices:
        try:
            # Try to connect to the device using Modbus
            client = ModbusTcpClient(device['ip'])
            if client.connect():
                print(f"PLC found at IP: {device['ip']}")
                client.close()
                return device['ip']
        except Exception as e:
            print(f"Error connecting to {device['ip']}: {e}")
            continue

    print("PLC not found in the network.")
    return None

# Function to send Modbus commands to the PLC
def send_modbus_commands(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print(f"Failed to connect to PLC at {plc_ip}")
            return

        # Example commands to control the fan and LEDs
        # Set Q_FAN (Fan Control) to TRUE
        client.write_coil(0, True)
        print("Fan Control (Q_FAN) set to TRUE")

        # Set Q_REDA (Fan A Red LED) to FALSE
        client.write_coil(4, False)
        print("Fan A Red LED (Q_REDA) set to FALSE")

        # Set Q_GREENA (Fan A Green LED) to TRUE
        client.write_coil(5, True)
        print("Fan A Green LED (Q_GREENA) set to TRUE")

        # Close the connection
        client.close()
    except ModbusIOException as e:
        print(f"Modbus IO Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function
def main():
    # Define the target IP range for scanning
    target_ip_range = "192.168.9.0/24"

    # Find the PLC's IP address
    plc_ip = find_plc_ip(target_ip_range)
    if plc_ip:
        # Send Modbus commands to the PLC
        send_modbus_commands(plc_ip)

if __name__ == "__main__":
    main()