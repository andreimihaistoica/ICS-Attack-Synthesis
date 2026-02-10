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

# Function to modify the tasking of the PLC
def modify_tasking():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the current tasking configuration
            tasking_config = conn.read(['Tasking_Config'])
            print("Current tasking configuration:", tasking_config)
            
            # Modify the tasking configuration
            new_tasking_config = {'Task1': {'Interval': 10, 'Frequency': 100, 'Priority': 1},
                                  'Task2': {'Interval': 20, 'Frequency': 50, 'Priority': 2}}
            conn.write(['Tasking_Config'], [new_tasking_config])
            print("Tasking configuration modified")
    else:
        print("PLC IP address not found")

# Function to create a new task association
def create_task_association():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Create a new task association
            new_task_association = {'Task': 'Task3', 'Program': 'Prog2'}
            conn.write(['Task_Associations'], [new_task_association])
            print("New task association created")
    else:
        print("PLC IP address not found")

# Main function to start the modification of controller tasking
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Modify the tasking of the PLC
        modify_tasking()
        
        # Create a new task association
        create_task_association()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()