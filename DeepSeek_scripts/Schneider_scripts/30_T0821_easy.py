import snap7
from snap7.util import *
import socket

def find_plc_ip():
    # Simulate finding the PLC's IP address (replace with actual discovery logic)
    # For example, you could use ARP scanning or other network discovery tools.
    plc_ip = "192.168.0.1"  # Replace with actual IP or discovery logic
    print(f"Found PLC IP: {plc_ip}")
    return plc_ip

def modify_controller_tasking(plc_ip):
    try:
        # Create a Snap7 client
        client = snap7.client.Client()

        # Connect to the PLC
        client.connect(plc_ip, 0, 1)
        print(f"Connected to PLC at {plc_ip}")

        # Example: Modify tasking by associating a new program with OB1
        # This is a simplified example. Actual implementation depends on the PLC's API.
        # Here, we assume we are modifying the task association in the PLC's memory.

        # Step 1: Read the current task configuration (e.g., OB1)
        ob1_data = client.db_read(1, 0, 100)  # Read 100 bytes from DB1 (example)
        print("Current OB1 Data:", ob1_data)

        # Step 2: Modify the tasking (e.g., associate a new program)
        # For example, write a new program to the PLC's memory
        new_program = bytearray([0x01, 0x02, 0x03, 0x04])  # Example program
        client.db_write(1, 0, new_program)
        print("New program written to PLC.")

        # Step 3: Associate the new program with OB1
        # Modify the task association in the PLC's memory
        task_association = bytearray([0x01])  # Example: Associate with OB1
        client.db_write(1, 10, task_association)
        print("Task association modified.")

        # Step 4: Verify the changes
        updated_ob1_data = client.db_read(1, 0, 100)
        print("Updated OB1 Data:", updated_ob1_data)

        # Disconnect from the PLC
        client.disconnect()
        print("Disconnected from PLC.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Modify the controller tasking
    modify_controller_tasking(plc_ip)