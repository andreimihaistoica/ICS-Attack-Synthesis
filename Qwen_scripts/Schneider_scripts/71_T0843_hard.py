import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to find the PLC's IP address
def find_plc_ip():
    ip_range = "192.168.9.0/24"
    plc_ip = None

    # Scan the IP range to find the PLC
    for ip in ip_range.split('/'):
        if ip == '0':
            continue
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((f"192.168.9.{ip}", 502))  # Modbus TCP port
                if result == 0:
                    plc_ip = f"192.168.9.{ip}"
                    break
        except socket.error:
            continue

    return plc_ip

# Function to check the PLC's operating mode
def check_operating_mode(plc_ip):
    with LogixDriver(plc_ip) as plc:
        try:
            status = plc.get_plc_status()
            return status['state']
        except Exception as e:
            print(f"Error checking operating mode: {e}")
            return None

# Function to perform an online edit
def perform_online_edit(plc_ip):
    with LogixDriver(plc_ip) as plc:
        try:
            # Change the operating mode to PROGRAM if necessary
            if check_operating_mode(plc_ip) != 'PROGRAM':
                plc.set_plc_mode('PROGRAM')

            # Perform the online edit
            # Example: Modify the M_ACTFAN variable to TRUE
            plc.write('M_ACTFAN', True)

            # Change the operating mode back to RUN
            plc.set_plc_mode('RUN')

            print("Online edit successful.")
        except Exception as e:
            print(f"Error performing online edit: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        operating_mode = check_operating_mode(plc_ip)
        if operating_mode:
            print(f"PLC operating mode: {operating_mode}")
            perform_online_edit(plc_ip)
        else:
            print("Failed to check operating mode.")
    else:
        print("PLC not found in the specified IP range.")

if __name__ == "__main__":
    main()