import subprocess
import socket
import ipaddress
import time

# --- CONFIGURATION ---
DEFAULT_GATEWAY = "192.168.1.1"  # Your network's default gateway
SUBNET_MASK = "255.255.255.0" # Your network's subnet mask
NETWORK_BASE = "192.168.1." # Base IP address of the network.  Used if gateway ping fails
IP_RANGE_START = 1  # Starting IP address in the range to scan
IP_RANGE_END = 254  # Ending IP address in the range to scan
POSSIBLE_PLC_PORTS = [502, 44818, 102] # Common PLC Ports: Modbus (502), Ethernet/IP (44818), S7 (102)
DEFAULT_CREDENTIALS = [
    ("", ""),  # No username, no password
    ("admin", "admin"),
    ("administrator", "password"),
    ("root", "root"),
    ("plc", "plc"),
    ("PlcUser", "PlcUser"),  # Siemens
    ("Operator", "Operator") # Siemens
    # Add more default credentials here
]
PLC_PROTOCOL = "Modbus" # Change to the protocol used by your PLC (e.g., Modbus, Ethernet/IP, S7)
# --- END CONFIGURATION ---

def plc_connect(ip_address, port):
    """
    Connects to the PLC at the given IP address and port.
    Replace this with code specific to your PLC's protocol.
    Example (Modbus TCP):
    from pymodbus.client import ModbusTcpClient
    try:
        client = ModbusTcpClient(ip_address, port=port)
        client.connect()
        return client
    except Exception as e:
        print(f"Error connecting to {ip_address}:{port}: {e}")
        return None
    """
    print(f"Attempting to connect to {ip_address}:{port} using {PLC_PROTOCOL} (Placeholder)")
    # Replace with your actual connection logic
    # time.sleep(1) # simulate connection delay
    return True # Indicate successful connection (replace with actual result)

def plc_login(connection, username, password):
    """
    Attempts to log in to the PLC using the given username and password.
    Replace this with code specific to your PLC's protocol.
    Example (Hypothetical Modbus Authentication - unlikely):
    try:
        # Implement your Modbus authentication logic here. This is highly simplified.
        # Modbus generally doesn't have explicit username/password authentication
        # but you might simulate it by writing to specific registers.
        if username == "admin" and password == "admin":
            return True  # Successful login
        else:
            return False # Incorrect credentials
    except Exception as e:
        print(f"Error logging in with {username}:{password}: {e}")
        return False
    """
    print(f"Attempting to login with {username}:{password} (Placeholder)")
    # Replace with your actual login logic
    # time.sleep(1) # simulate login delay
    return True # Indicate successful login (replace with actual result)

def plc_disconnect(connection):
    """
    Disconnects from the PLC.
    Replace this with code specific to your PLC's protocol.
    Example (Modbus TCP):
    try:
        connection.close()
    except Exception as e:
        print(f"Error disconnecting: {e}")
    """
    print("Disconnecting (Placeholder)")
    # Replace with your actual disconnection logic
    # time.sleep(1) # simulate disconnection delay
    return True

def ping(host):
    """Pings a host and returns True if successful, False otherwise."""
    try:
        # Use -n 1 for Windows, -c 1 for Linux/macOS to send only one packet
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Ping error: {e}")
        return False


def discover_plc_ip_address():
    """
    Attempts to discover the PLC's IP address.
    Returns the IP address if found, None otherwise.
    """
    print("Attempting to discover PLC IP address...")

    # 1. Try pinging the default gateway
    if ping(DEFAULT_GATEWAY):
        print(f"Default gateway {DEFAULT_GATEWAY} is reachable.  Assuming PLC is on the same network.")
    else:
        print(f"Default gateway {DEFAULT_GATEWAY} is unreachable.  Continuing with network scan.")

    # 2. Network Scan using nmap
    try:
        ip_network = ipaddress.ip_network(NETWORK_BASE + "0/" + SUBNET_MASK, strict=False)
        network_address = str(ip_network.network_address)
        cidr = str(ip_network.prefixlen)

        # Construct the nmap command to scan the network for open PLC ports
        nmap_command = [
            "nmap",
            "-p", ",".join(map(str, POSSIBLE_PLC_PORTS)),  # Scan common PLC ports
            "-T4",  # Aggressive timing
            "-F", # Fast Scan
            network_address + "/" + cidr
        ]
        print(f"Running nmap: {' '.join(nmap_command)}")
        result = subprocess.run(nmap_command, capture_output=True, text=True, timeout=60) # Increased timeout

        if result.returncode == 0:
            nmap_output = result.stdout
            print(f"Nmap Output:\n{nmap_output}")

            # Parse nmap output to find potential PLC IP addresses
            for line in nmap_output.splitlines():
                if "open" in line and any(str(port) in line for port in POSSIBLE_PLC_PORTS):
                    parts = line.split()
                    if len(parts) > 1:
                        ip_address = parts[1]
                        print(f"Found potential PLC IP address: {ip_address}")
                        return ip_address

        else:
            print(f"Nmap scan failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"Error during network scan: {e}")
        return None

    print("PLC IP address discovery failed.")
    return None



if __name__ == "__main__":
    import platform  # Import inside `if __name__ == "__main__":`
    plc_ip_address = discover_plc_ip_address()

    if not plc_ip_address:
        print("Could not discover PLC IP address.  Exiting.")
        exit()

    print(f"Attempting default credential login on PLC at: {plc_ip_address}")

    for port in POSSIBLE_PLC_PORTS:
        print(f"Trying port: {port}")
        connection = plc_connect(plc_ip_address, port)
        if connection:
            for username, password in DEFAULT_CREDENTIALS:
                print(f"Trying username: {username}, password: {password}")
                if plc_login(connection, username, password):
                    print(f"Successfully logged in with username: {username}, password: {password} on port {port}!")
                    plc_disconnect(connection)
                    exit() # Exit after first successful login

                else:
                    print("Login failed.")
            plc_disconnect(connection)
        else:
            print(f"Connection to {plc_ip_address}:{port} failed.")

    print("All login attempts failed.")