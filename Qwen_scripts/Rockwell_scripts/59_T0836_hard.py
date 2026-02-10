import pycomm3
import socket
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same network and has a static IP
    # You can use a network scanner to find the IP address
    # For simplicity, we will use a hardcoded IP address
    return '192.168.1.10'  # Replace with the actual IP address of your PLC

# Function to modify the TONOFF_1.PT parameter
def modify_parameter(plc_ip, new_value):
    try:
        # Create a PLC object
        plc = pycomm3.LogixDriver(plc_ip)
        
        # Open the connection to the PLC
        plc.open()
        
        # Modify the TONOFF_1.PT parameter
        plc.write((('TONOFF_1.PT', new_value),))
        
        # Close the connection
        plc.close()
        
        print(f"Parameter TONOFF_1.PT modified to {new_value}")
    except Exception as e:
        print(f"Error modifying parameter: {e}")

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    
    # Define the new value for the TONOFF_1.PT parameter
    new_value = T#5S  # Change this to the desired value
    
    # Modify the parameter
    modify_parameter(plc_ip, new_value)

if __name__ == "__main__":
    main()