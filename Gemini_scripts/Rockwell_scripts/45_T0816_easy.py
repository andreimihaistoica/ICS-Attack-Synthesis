import snap7
import subprocess
import socket
import time

# CONFIGURATION - Adjust these values based on your specific setup
SWITCH_IP = "YOUR_SWITCH_IP"  # Example: "192.168.1.10"
ENGINEERING_WORKSTATION_IP = "YOUR_ENGINEERING_WORKSTATION_IP" # Example: "192.168.1.100"
PLC_RACK = 0
PLC_SLOT = 1

#---------------------------------------------------------------
# PLC IP Discovery Function (Attempts to find PLC IP address)
# This function pings known possible devices to narrow down the PLC's IP.
# Adapt and expand the pinged range based on your network setup.
#---------------------------------------------------------------

def find_plc_ip(switch_ip, workstation_ip):
    """
    Attempts to automatically discover the PLC's IP address by process of elimination
    """

    # 1. Determine the Network Segment and Possible Range
    network_segment = '.'.join(switch_ip.split('.')[:-1]) + '.'  #Assumes same /24 network as switch
    print(f"Scanning network segment: {network_segment}")

    # 2. Define a Range of IPs to Scan (Expand this range if necessary)
    possible_ips = [network_segment + str(i) for i in range(1, 255)]

    # 3. Remove Known IPs (Switch, Engineering Workstation, and this machine)
    possible_ips = [ip for ip in possible_ips if ip not in [switch_ip, workstation_ip, socket.gethostbyname(socket.gethostname())]]  #Get own IP

    # 4. Ping Each IP and Check for a Response
    for ip in possible_ips:
        try:
            print(f"Pinging {ip}...")
            # Use subprocess for reliable ping across OS
            ping_reply = subprocess.run(['ping', '-n', '1', '-w', '500', ip], # -n 1 (Windows) or -c 1 (Linux/macOS) -w timeout
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=1) # Added timeout for faster scanning
            if ping_reply.returncode == 0:  # Successful ping
                print(f"  {ip} responded to ping.")
                #Further validation could be performed (e.g., trying to connect via Snap7).
                return ip #Assume this is the PLC for now

        except subprocess.TimeoutExpired:
            print(f"  {ip} ping timed out.") # Handle timeout gracefully
        except Exception as e:
            print(f"  Error pinging {ip}: {e}")
            # Handle exceptions like invalid IP addresses or network errors.

    print("PLC IP address not found in the defined range.  Adjust the IP scanning range.")
    return None


#---------------------------------------------------------------
# Snap7 PLC Restart Function
#---------------------------------------------------------------
def restart_plc(plc_ip, rack, slot):
    """
    Attempts to restart the PLC using Snap7.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Send the PLC Stop command
        plc.plc_stop()
        print(f"PLC at {plc_ip} stopped.")

        # Wait for a short period before attempting to start
        time.sleep(5)  # Adjust this delay as needed

        # Send the PLC Start command
        plc.plc_start()
        print(f"PLC at {plc_ip} started.")

        plc.disconnect()  # Important: Disconnect after use!
        return True

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error restarting PLC: {e}")
        return False
    except Exception as e:
        print(f"General error: {e}")
        return False

#---------------------------------------------------------------
# Main Script Execution
#---------------------------------------------------------------

if __name__ == "__main__":
    # 1. Discover PLC IP Address (if needed)
    PLC_IP = find_plc_ip(SWITCH_IP, ENGINEERING_WORKSTATION_IP)

    if PLC_IP:
        print(f"PLC IP address found: {PLC_IP}")

        # 2. Attempt to Restart the PLC
        if restart_plc(PLC_IP, PLC_RACK, PLC_SLOT):
            print("PLC restart attempt completed.")
        else:
            print("PLC restart attempt failed.")
    else:
        print("Failed to automatically discover PLC IP address.  Check network configuration and script settings.")