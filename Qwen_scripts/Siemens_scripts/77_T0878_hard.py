import socket
import logging
from pycomm3 import LogixDriver, S7Client

# Configure logging
logging.basicConfig(filename='alarm_suppression.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the PLC
            with S7Client(ip) as client:
                if client.get_connected():
                    logging.info(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            logging.error(f"Error connecting to {ip}: {e}")
    logging.error("PLC not found on the network.")
    return None

# Function to suppress alarms
def suppress_alarms(plc_ip):
    try:
        with S7Client(plc_ip) as client:
            if client.get_connected():
                # Suppress Fan A and Fan B alarms
                client.write_by_name("Activate_Fan_A", False)
                client.write_by_name("Activate_Fan_B", False)
                client.write_by_name("Overheating_Check", False)
                client.write_by_name("Fan_A_Red", False)
                client.write_by_name("Fan_B_Red", False)
                client.write_by_name("Fan_A_Green", False)
                client.write_by_name("Fan_B_Green", False)
                client.write_by_name("Tag_2", False)
                client.write_by_name("Master_Fan_B_HMI", False)
                logging.info("Alarms suppressed successfully.")
            else:
                logging.error("Failed to connect to the PLC.")
    except Exception as e:
        logging.error(f"Error suppressing alarms: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()