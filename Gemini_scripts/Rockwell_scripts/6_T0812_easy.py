import socket
import ipaddress
from pycomm3 import LogixDriver
import time  # For delays
import subprocess

# Configuration
DEFAULT_CREDS = {
    "Allen-Bradley": [
        {"username": "Administrator", "password": ""},  # Common default for some A-B PLCs
        {"username": "admin", "password": "password"}, #Another example
        # Add more Allen-Bradley defaults here
    ],
    "Siemens": [
        {"username": "admin", "password": "admin"},  # Example Siemens default (check specific model)
        # Add more Siemens defaults here
    ],
    # Add default credentials for other PLC brands here
}

PLC_BRAND = "Allen-Bradley"  # Change if needed

# --- Function to discover PLC IP address (basic network scan) ---
def discover_plc_ip():
    """
    Attempts to discover the PLC IP address by pinging a range of IPs within the local network.
    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Get local network information using ipconfig (Windows)
        output = subprocess.check_output(["ipconfig"]).decode("utf-8")
        for line in output.splitlines():
            if "IPv4 Address" in line:
                ip_address = line.split(":")[1].strip()
            if "Subnet Mask" in line:
                subnet_mask = line.split(":")[1].strip()

        network = ipaddress.ip_network(f"{ip_address}/{subnet_mask}", strict=False)

        # Ping scan range
        for ip in network.hosts():
            ip = str(ip)
            response = subprocess.call(["ping", "-n", "1", "-w", "200", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Windows ping
            if response == 0:
                #TODO find how to make this part more robust, like check ports
                print(f"Possible PLC IP Address: {ip}")
                return ip
            else:
                print("No IP address was found")
                return None

    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None

# --- Function to attempt login with default credentials ---
def attempt_login(plc_ip, username, password):
    """
    Attempts to connect to the PLC using the provided username and password.
    Returns:
        bool: True if login is successful, False otherwise.
    """
    try:
        with LogixDriver(plc_ip) as comm:
            comm.Timeout = 5 #shorten timeout
            comm.IPAddress = plc_ip
            comm.Port = 44818 #Common for Rockwell

            try:
                comm.Open() #attempting connection
                print(f"Successfully connected to {plc_ip} with {username}:{password}")
                return True
            except Exception as e:
                print(f"Login attempt failed for {username}:{password}. Error: {e}")
                return False

    except Exception as e:
        print(f"Error connecting to PLC at {plc_ip}: {e}")
        return False
# --- Main script execution ---
if __name__ == "__main__":
    plc_ip = discover_plc_ip()

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")

        credentials = DEFAULT_CREDS.get(PLC_BRAND) #Change the brand as needed
        if credentials:
            for cred in credentials:
                username = cred["username"]
                password = cred["password"]
                if attempt_login(plc_ip, username, password):
                    print(f"[+] Successfully logged in to PLC {plc_ip} using default credentials: {username}:{password}")
                    #ADD LOGIC TO CHANGE PASSWORD, that would require knowing what the engineering workstation does and mimicking those requests to the PLC
                    exit(0)  # Exit after successful login
        else:
            print(f"No default credentials found for PLC brand: {PLC_BRAND}")
    else:
        print("Could not discover PLC IP address. Please specify it manually.")