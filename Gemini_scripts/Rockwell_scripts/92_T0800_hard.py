import pycomm3
import time
import subprocess
import re

# Configuration -  Adjust these values as needed
PLC_CONTROLLER_TAG_NAME = "Tog_Off"  # Tag to control the "Tog_Off" variable
PLC_IP_DISCOVERY_METHOD = "arp-scan" # or "nmap" or "manual"

def discover_plc_ip_address(method="arp-scan"):
    """
    Attempts to discover the PLC's IP address using various methods.
    Prioritizes reliability, but may require system dependencies.

    Args:
        method (str):  "arp-scan", "nmap", or "manual".  Chooses the discovery method.

    Returns:
        str: The IP address of the PLC, or None if discovery fails.
    """
    if method == "arp-scan":
        try:
            # Requires arp-scan to be installed (sudo apt install arp-scan on Linux)
            result = subprocess.check_output(["arp-scan", "--localnet"], text=True)  # Captures output as text
            # Example arp-scan output:
            # Interface: eth0, type: EN10MB, MAC: 00:11:22:33:44:55, IPv4: 192.168.1.10
            # Starting arp-scan 1.9.7 with 256 hosts (http://www.nta-monitor.com/tools/arp-scan/)
            # 192.168.1.1    00:0a:95:9d:68:16       Allen-Bradley
            # ...
            for line in result.splitlines():
                if "Allen-Bradley" in line:  # Identify Rockwell/Allen-Bradley devices
                    ip_address = line.split()[0]
                    print(f"PLC IP address found using arp-scan: {ip_address}")
                    return ip_address
            print("PLC IP address not found using arp-scan. Check arp-scan installation and network.")
            return None

        except FileNotFoundError:
            print("Error: arp-scan not found. Please install it (e.g., sudo apt install arp-scan).")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error executing arp-scan: {e}")
            return None


    elif method == "nmap":
        try:
             # Requires nmap to be installed (sudo apt install nmap on Linux)
            result = subprocess.check_output(["nmap", "-p", "44818", "192.168.1.0/24"], text=True) #Common port for Ethernet/IP
            # Example nmap output:
            # Starting Nmap 7.93 ( https://nmap.org ) at 2024-11-02 14:38 EDT
            # Nmap scan report for 192.168.1.10
            # Host is up (0.00050s latency).
            #
            # PORT      STATE SERVICE
            # 44818/tcp open  ethernetip-1

            for line in result.splitlines():
                if "ethernetip-1" in line and "open" in line:
                    ip_address = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', result)
                    if ip_address:
                        print(f"PLC IP address found using nmap: {ip_address.group(1)}")
                        return ip_address.group(1)
            print("PLC IP address not found using nmap. Check nmap installation and network.")
            return None
        except FileNotFoundError:
            print("Error: nmap not found. Please install it (e.g., sudo apt install nmap).")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error executing nmap: {e}")
            return None

    elif method == "manual":
        ip_address = input("Please enter the PLC's IP address manually: ")
        return ip_address
    else:
        print("Invalid IP discovery method specified.")
        return None


def toggle_firmware_update_mode(plc_ip, tag_name):
    """
    Simulates activating and deactivating a firmware update mode by toggling a specific PLC tag.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag_name (str): The name of the tag that controls the "firmware update mode".
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Read the current value of the tag
            status, current_value = plc.read(tag_name)
            if not status.startswith("Success"):
                print(f"Error reading tag {tag_name}: {status}")
                return

            current_value = current_value[0] # Extract the boolean value

            # Toggle the tag's value (activate update mode)
            new_value = not current_value
            status = plc.write(tag_name, new_value)

            if status == 'Success':
                print(f"Successfully set {tag_name} to {new_value} (Activating Firmware Update Mode).")
            else:
                print(f"Error writing to tag {tag_name}: {status}")
                return

            time.sleep(5)  # Simulate the device being in update mode

            # Toggle the tag's value back (deactivate update mode)
            status = plc.write(tag_name, current_value) # Set back to original value
            if status == 'Success':
                print(f"Successfully set {tag_name} back to {current_value} (Deactivating Firmware Update Mode).")
            else:
                print(f"Error writing to tag {tag_name}: {status}")
                return

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    plc_ip = discover_plc_ip_address(PLC_IP_DISCOVERY_METHOD)

    if plc_ip:
        toggle_firmware_update_mode(plc_ip, PLC_CONTROLLER_TAG_NAME)
    else:
        print("Failed to discover PLC IP address.  Exiting.")