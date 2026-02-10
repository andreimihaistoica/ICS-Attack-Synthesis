import pycomm3
from pycomm3 import LogixDriver, SLC500Driver, PLC
import netifaces as ni
import socket

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # Check if the IP is in the local network (e.g., 192.168.x.x)
            if ip.startswith('192.168'):
                # Try to connect to the PLC
                plc = PLC()
                if plc.open(ip):
                    print(f"PLC found at IP: {ip}")
                    plc.close()
                    return ip
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
    
    print("PLC not found on any network interface.")
    return None

# Function to read tags from the PLC
def read_plc_tags(plc_ip):
    try:
        with PLC() as plc:
            if plc.open(plc_ip):
                # Define the tags to read
                tags = [
                    "Fan_A", "Fan_B", "Fan_A_Red", "Fan_A_Green", "Fan_B_Red", "Fan_B_Green",
                    "System_Byte", "FirstScan", "DiagStatusUpdate", "AlwaysTRUE", "AlwaysFALSE",
                    "Clock_Byte", "Clock_10Hz", "Clock_5Hz", "Clock_2.5Hz", "Clock_2Hz",
                    "Clock_1.25Hz", "Clock_1Hz", "Clock_0.625Hz", "Clock_0.5Hz",
                    "Motor_Temp", "Activate_Fan_A", "Activate_Fan_B", "Master_Fan_B_HMI",
                    "Motor_Status", "Master_OFF", "Tag_1", "Overheating_Check", "Tag_2",
                    "Motor_Status_GET", "Tag_3", "Tag_4", "Tag_5"
                ]
                
                # Read the tags
                results = plc.read(*tags)
                
                # Print the results
                for tag, value in results:
                    print(f"{tag}: {value}")
            else:
                print(f"Failed to connect to PLC at IP: {plc_ip}")
    except Exception as e:
        print(f"Error reading tags: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Read tags from the PLC
        read_plc_tags(plc_ip)

if __name__ == "__main__":
    main()