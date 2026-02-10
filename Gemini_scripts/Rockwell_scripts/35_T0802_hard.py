import pycomm3
import time
import socket

# MITRE ATT&CK Technique: Collection: Automated Collection (T0009)

# Configurable Parameters
PLC_MODEL = "Micro850"  # Modify if necessary
OPC_SERVER_ADDRESS = "opc.tcp://localhost:4840"  # Example - Replace with your OPC server address if applicable.  Leave blank if not applicable to this PLC model.  Micro850 does *not* inherently support OPC UA.  If you've added an OPC UA server *connected* to the Micro850, then populate this.
SLEEP_TIME = 5  # Time in seconds between collection cycles
TAGS_TO_COLLECT = [
    "NewVariable",
    "Activate_FanA",
    "FanA_Timer",
    "START",
    "STOP",
    "TON_1.Q",
    "TONOFF_1.Q",
    "FanA_Off",
    "Tog_Off",
    "_IO_EM_DO_02",
    "_IO_EM_DO_06",
    "_IO_EM_DO_07"

]

# Function to find PLC IP Address (attempt to find it automatically)
def find_plc_ip():
    """Attempts to discover the PLC's IP address on the network."""
    # This is a very basic method and might not work in all network configurations.
    # Consider more robust discovery methods if needed.
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a public DNS server (doesn't actually send data)
        plc_ip = s.getsockname()[0]
        s.close()
        print(f"PLC IP address found (assumed to be same as workstation): {plc_ip}")  #informational message
        return plc_ip
    except Exception as e:
        print(f"Error finding PLC IP address: {e}")
        return None  # Indicate failure to find IP

# Function to collect data from Rockwell Micro850 PLC
def collect_data_micro850(plc_ip):
    """Collects data from a Rockwell Micro850 PLC using pycomm3."""

    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            print(f"Successfully connected to PLC at {plc_ip}")

            while True:
                data = plc.read(*TAGS_TO_COLLECT) #Unpacks the TAGS_TO_COLLECT

                if all(d.status == 'Success' for d in data): #Verify that all tags returned successfully
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"[{timestamp}] Data Collection:")
                    for tag_data in data:
                        print(f"  {tag_data.symbol}: {tag_data.value}")

                    # ---  Here is where you would add code to log or send the collected data ---
                    # Examples:
                    # 1. Write data to a log file:
                    #    with open("plc_data.log", "a") as f:
                    #       f.write(f"[{timestamp}] {data}\n")
                    #
                    # 2. Send data to a SIEM system (e.g., using HTTP or syslog)
                    #    This would require additional libraries and configuration.


                    time.sleep(SLEEP_TIME)
                else:
                    print("Error reading tags.  Check tag names and PLC connection.")
                    for tag_data in data:
                        if tag_data.status != 'Success':
                            print(f"  Error reading tag: {tag_data.symbol} - Status: {tag_data.status}")
                    break #Exit loop to avoid repeated errors

    except Exception as e:
        print(f"Error communicating with PLC: {e}")


# Main execution block
if __name__ == "__main__":
    plc_ip_address = find_plc_ip()

    if plc_ip_address:
        collect_data_micro850(plc_ip_address)
    else:
        print("Could not determine PLC IP address.  Exiting.")
        print("Please ensure the workstation is on the same network as the PLC, or manually configure the IP address.")