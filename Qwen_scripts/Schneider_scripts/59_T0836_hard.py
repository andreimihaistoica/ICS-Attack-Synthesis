import socket
import struct
import time
import minimalmodbus

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    subnet = '192.168.9.0/24'
    ip_list = [f"192.168.9.{i}" for i in range(1, 255)]
    
    for ip in ip_list:
        try:
            # Attempt to connect to the Modbus server on the PLC
            plc = minimalmodbus.Instrument(ip, 1)
            plc.serial.baudrate = 19200
            plc.serial.bytesize = 8
            plc.serial.parity = minimalmodbus.serial.PARITY_EVEN
            plc.serial.stopbits = 1
            plc.serial.timeout = 1
            
            # Read a register to check if the PLC is responsive
            response = plc.read_register(0, functioncode=3)
            print(f"PLC found at IP: {ip}")
            return ip
        except Exception as e:
            continue
    return None

# Function to modify the PLC parameters
def modify_plc_parameters(plc_ip):
    try:
        # Connect to the PLC
        plc = minimalmodbus.Instrument(plc_ip, 1)
        plc.serial.baudrate = 19200
        plc.serial.bytesize = 8
        plc.serial.parity = minimalmodbus.serial.PARITY_EVEN
        plc.serial.stopbits = 1
        plc.serial.timeout = 1
        
        # Modify the counter preset value to a higher value
        new_preset_value = 100  # Example: Change the counter preset from 15 to 100
        plc.write_register(0, new_preset_value, functioncode=6)
        print(f"Modified counter preset value to {new_preset_value}")
        
        # Modify the timer preset value to a shorter duration
        new_timer_value = 5  # Example: Change the timer preset from 20 seconds to 5 seconds
        plc.write_register(1, new_timer_value, functioncode=6)
        print(f"Modified timer preset value to {new_timer_value} seconds")
        
    except Exception as e:
        print(f"Error modifying PLC parameters: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Modify the PLC parameters
        modify_plc_parameters(plc_ip)
    else:
        print("PLC not found on the network")

if __name0.1 == "__main__":
    main()