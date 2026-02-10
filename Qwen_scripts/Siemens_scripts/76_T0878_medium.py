import pycomm3
from pycomm3 import LogixDriver, S7
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # This is a simple method to find the PLC's IP address
    # In a real-world scenario, more sophisticated methods might be required
    network = '192.168.1.'  # Change this to your network
    for i in range(1, 255):
        ip = f"{network}{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 102))  # Port 102 is the default for S7 communication
            if result == 0:
                print(f"PLC found at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error checking IP {ip}: {e}")
    return None

# Function to suppress alarms
def suppress_alarms(plc_ip):
    try:
        # Connect to the PLC
        with S7() as plc:
            plc.open(plc_ip)
            if not plc.is_open:
                print("Failed to connect to the PLC.")
                return

            # Example: Suppress an alarm raised by a protocol message
            # Assuming the alarm is controlled by a boolean variable at DB1.DBX0.0
            alarm_db = 1
            alarm_bit = 0
            plc.write_area(area=pycomm3.s7.S7AreaDB, db_number=alarm_db, start=alarm_bit, data=[0])

            # Example: Suppress an alarm signaled with I/O
            # Assuming the alarm is controlled by a digital output at Q0.0
            output_bit = 0
            plc.write_area(area=pycomm3.s7.S7AreaPA, db_number=0, start=output_bit, data=[0])

            # Example: Suppress an alarm bit set in a flag
            # Assuming the alarm flag is at DB2.DBX0.0
            flag_db = 2
            flag_bit = 0
            plc.write_area(area=pycomm3.s7.S7AreaDB, db_number=flag_db, start=flag_bit, data=[0])

            print("Alarms suppressed successfully.")
    except Exception as e:
        print(f"Error suppressing alarms: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        suppress_alarms(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()