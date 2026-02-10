import pycomm3
import socket
import subprocess

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use ARP scan to find devices on the network
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'dynamic' in line:
            ip = line.split()[0]
            try:
                # Attempt to connect to the IP to see if it's the PLC
                with pycomm3.CipDriver(ip) as driver:
                    if driver.open():
                        print(f"PLC found at IP: {ip}")
                        return ip
            except Exception as e:
                print(f"Failed to connect to {ip}: {e}")
    print("PLC not found on the network.")
    return None

# Function to change the operating mode of the PLC
def change_operating_mode(plc_ip, new_mode):
    with pycomm3.CipDriver(plc_ip) as driver:
        if driver.open():
            print(f"Connected to PLC at {plc_ip}")
            try:
                # Change the operating mode
                response = driver.send_unit_data({
                    'service': pycomm3.services.ServiceCodes.ChangeState,
                    'class_code': pycomm3.cip.CIPTypes.ObjectType,
                    'instance': 1,
                    'attribute': 1,
                    'request_data': new_mode
                })
                if response['status'] == 0:
                    print(f"Operating mode changed to {new_mode}")
                else:
                    print(f"Failed to change operating mode: {response['status']}")
            except Exception as e:
                print(f"Error changing operating mode: {e}")
        else:
            print(f"Failed to connect to PLC at {plc_ip}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Change the operating mode to "Program" (mode 1)
        change_operating_mode(plc_ip, 1)

if __name__ == "__main__":
    main()