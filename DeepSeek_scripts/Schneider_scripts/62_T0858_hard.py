from pycomm3 import LogixDriver

def find_plc_ip():
    # Placeholder function to find the PLC's IP address
    # This could be implemented using network scanning tools or manual input
    # For simplicity, we'll use the provided IP address
    return "192.168.9.24"

def change_plc_mode(ip_address):
    try:
        # Connect to the PLC
        plc = LogixDriver(ip_address)
        plc.open()

        # Get the current operating mode
        current_mode = plc.get_plc_mode()
        print(f"Current PLC Mode: {current_mode}")

        # Change the operating mode to Program
        plc.set_plc_mode('program')
        print("Changed PLC Mode to Program")

        # Verify the new operating mode
        new_mode = plc.get_plc_mode()
        print(f"New PLC Mode: {new_mode}")

        # Close the connection
        plc.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"PLC IP Address: {plc_ip}")

    # Change the PLC's operating mode
    change_plc_mode(plc_ip)