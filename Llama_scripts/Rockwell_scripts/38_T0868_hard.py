from cpppo.server.enip import client
import socket
import time

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to detect the PLC's operating mode
def detect_operating_mode():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the PLC's operating mode
            operating_mode = conn.read(['Operating_Mode'])
            print("Operating mode:", operating_mode)
            
            # Determine the current operating mode
            if operating_mode == 'Program':
                print("PLC is in program mode. Changes can be made to the device's program.")
            elif operating_mode == 'Run':
                print("PLC is in run mode. Execution of the device's program is occurring.")
            elif operating_mode == 'Remote':
                print("PLC is in remote mode. Remote changes to the PLC's operation mode are allowed.")
            elif operating_mode == 'Stop':
                print("PLC is in stop mode. The PLC and program are stopped, and outputs are forced off.")
            elif operating_mode == 'Reset':
                print("PLC is in reset mode. Conditions on the PLC are reset to their original states.")
            elif operating_mode == 'Test/Monitor':
                print("PLC is in test/monitor mode. I/O is processed, and monitoring, force set, resets, and more are allowed.")
            else:
                print("Unknown operating mode.")
    else:
        print("PLC IP address not found")

# Function to monitor the PLC's operating mode
def monitor_operating_mode():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Monitor the PLC's operating mode
            while True:
                operating_mode = conn.read(['Operating_Mode'])
                print("Operating mode:", operating_mode)
                time.sleep(1)
    else:
        print("PLC IP address not found")

# Main function to start the detection of operating mode
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Detect the PLC's operating mode
        detect_operating_mode()
        
        # Monitor the PLC's operating mode
        monitor_operating_mode()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()