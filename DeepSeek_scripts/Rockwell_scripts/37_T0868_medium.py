from pycomm3 import LogixDriver
import socket

def find_plc_ip():
    # This is a placeholder function to simulate finding the PLC's IP address.
    # In a real-world scenario, you might use network scanning tools or DHCP logs.
    # For this example, we'll assume the PLC's IP is known or manually entered.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def detect_operating_mode(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Query the PLC's operating mode
            operating_mode = plc.get_plc_mode()
            print(f"PLC Operating Mode: {operating_mode}")
            
            # Additional details about the operating mode
            if operating_mode == 'Program':
                print("Mode: Program - PLC is in programming mode. Program uploads/downloads are enabled.")
            elif operating_mode == 'Run':
                print("Mode: Run - PLC is executing the program. Program uploads/downloads are disabled.")
            elif operating_mode == 'Remote':
                print("Mode: Remote - Remote changes to the PLC's operation mode are allowed.")
            elif operating_mode == 'Stop':
                print("Mode: Stop - PLC and program are stopped. Outputs are forced off.")
            elif operating_mode == 'Reset':
                print("Mode: Reset - PLC conditions are reset to their original states.")
            elif operating_mode == 'Test/Monitor':
                print("Mode: Test/Monitor - PLC is in test/monitor mode. I/O processing is active.")
            else:
                print("Unknown mode detected.")
    
    except Exception as e:
        print(f"Error detecting PLC operating mode: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    # Step 2: Detect the operating mode
    detect_operating_mode(plc_ip)