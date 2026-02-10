import pycomm3
import time
import os
import socket  # For finding IP address


def find_plc_ip():
    """
    Attempts to find the PLC's IP address.  This is a very basic approach
    and might not work in all network configurations.  You might need to
    replace this with a more robust IP discovery method for your specific setup.

    Returns:
        str: The IP address of the PLC, or None if it can't be found.
    """
    try:
        # Attempt to resolve the PLC's hostname (replace 'Micro850-PLC' with the actual hostname if needed)
        plc_hostname = "Micro850-PLC"  # Replace with your PLC's hostname
        plc_ip = socket.gethostbyname(plc_hostname)
        print(f"PLC IP address found: {plc_ip}")
        return plc_ip
    except socket.gaierror:
        print("Could not resolve PLC hostname.  Ensure the hostname is correct and DNS is configured properly.")
        return None
    except Exception as e:
        print(f"Error finding PLC IP address: {e}")
        return None


def inhibit_alarm(plc_ip, tag_to_inhibit):
    """
    Inhibits an alarm by manipulating PLC tags.

    Args:
        plc_ip (str): The IP address of the Rockwell Micro850 PLC.
        tag_to_inhibit (str): The name of the BOOL tag controlling the alarm/alarm condition.
    """

    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Check if the connection was successful
            if not plc.connected:
                print(f"Failed to connect to PLC at {plc_ip}.  Check IP address and network connectivity.")
                return

            # Read the initial value of the tag
            read_result = plc.read(tag_to_inhibit)
            if read_result.status == 'Success':
                initial_value = read_result.value
                print(f"Initial value of {tag_to_inhibit}: {initial_value}")
            else:
                print(f"Failed to read tag {tag_to_inhibit}. Status: {read_result.status}")
                return

            # Invert the tag to suppress the alarm (assuming a FALSE value disables the alarm).  Or force it to a value that disables the alarm
            # This depends on the logic.  If the alarm is active when TRUE, set it to FALSE.  If active when FALSE, set it to TRUE.
            # Here, we assume alarm active when TRUE, so we set it to FALSE.
            new_value = False

            write_result = plc.write(tag_to_inhibit, new_value)
            if write_result.status == 'Success':
                print(f"Successfully inhibited alarm by setting {tag_to_inhibit} to {new_value}")
            else:
                print(f"Failed to inhibit alarm. Status: {write_result.status}")

            # Optional: Verify the change (read the tag again)
            verify_result = plc.read(tag_to_inhibit)
            if verify_result.status == 'Success':
                verified_value = verify_result.value
                print(f"Verified value of {tag_to_inhibit}: {verified_value}")
                if verified_value != new_value:
                    print("WARNING: Write verification failed!  Tag value does not match expected value.")
            else:
                print(f"Failed to verify tag {tag_to_inhibit}. Status: {verify_result.status}")

    except Exception as e:
        print(f"An error occurred: {e}")



def main():
    """
    Main function to execute the alarm inhibition script.
    """

    plc_ip = find_plc_ip()

    if not plc_ip:
        print("PLC IP address not found. Exiting.")
        return

    # Choose the tag to inhibit (the one that controls the Red LED, as that's a clear visual indicator)
    tag_to_inhibit = "FanA_Off"  #  Controls Red LED

    # Inhibit the alarm
    inhibit_alarm(plc_ip, tag_to_inhibit)


if __name__ == "__main__":
    main()