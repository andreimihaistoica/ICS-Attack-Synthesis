import snap7
import socket
import re

def find_plc_ip_address():
    """
    Attempts to find the PLC's IP address by attempting to connect to common ports.
    Returns: The PLC's IP address as a string, or None if not found.
    """

    possible_ports = [502, 20000, 2000, 44818, 5000, 102]  # Common PLC ports
    for ip in ["192.168.9.24"]:
        for port in possible_ports:
            try:
                # Create a socket object
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)  # Set a timeout to avoid indefinite blocking

                # Attempt to connect
                s.connect((ip, port))
                print(f"Successfully connected to {ip}:{port}")
                s.close()
                return ip  # Return the IP if connection is successful
            except (socket.error, socket.timeout) as e:
                print(f"Connection to {ip}:{port} failed: {e}")
                s.close()
    print("Warning: Returning manually given IP address")
    return "192.168.9.24"

def collect_tags_and_values(plc_ip, rack=0, slot=1):
    """
    Collects tag names, addresses, and values from the Schneider Electric TM221CE16R PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.

    Returns:
        dict: A dictionary containing tag information. The keys of the dictionary
              are the tag symbols (names), and the values are dictionaries containing
              the address and current value.
              Returns None if there's an error connecting to the PLC.
    """

    try:
        plc = snap7.client.Client()
        plc.set_as_tcp_client()
        plc.connect(plc_ip, rack, slot)
        print(f"Connected to PLC at {plc_ip}, Rack={rack}, Slot={slot}")

        tag_data = {}

        # Define the tags to collect (based on the provided structured text)
        tags = {
            "M_ACTFAN": {"area": snap7.types.Areas.MK, "start": 1, "size": 1, "type": "BOOL"},
            "M_TOG": {"area": snap7.types.Areas.MK, "start": 2, "size": 1, "type": "BOOL"},
            "Q_FAN": {"area": snap7.types.Areas.PE, "start": 0, "size": 1, "type": "BOOL"},
            "Q_REDA": {"area": snap7.types.Areas.PE, "start": 4, "size": 1, "type": "BOOL"},
            "Q_GREENA": {"area": snap7.types.Areas.PE, "start": 5, "size": 1, "type": "BOOL"},
            "SB_TB1S": {"area": snap7.types.Areas.SYS, "start": 6, "size": 1, "type": "BOOL"},
            "Counter0": {"area": snap7.types.Areas.CT, "start": 0, "size": 2, "type": "INT"},  # Assuming CTU is represented as an integer value
            "Timer0": {"area": snap7.types.Areas.TM, "start": 0, "size": 2, "type": "INT"},  # Assuming TP is represented as an integer value
            "Timer1": {"area": snap7.types.Areas.TM, "start": 1, "size": 2, "type": "INT"},  # Assuming TON is represented as an integer value
        }

        for tag_name, tag_info in tags.items():
            try:
                area = tag_info["area"]
                start = tag_info["start"]
                size = tag_info["size"]
                data_type = tag_info["type"]
                
                # Read the data
                if data_type == "BOOL":
                    byte_index = start // 8
                    bit_index = start % 8
                    byte_data = plc.read_area(area, 0, byte_index, 1)
                    value = snap7.util.get_bool(byte_data, 0, bit_index)
                else:
                     value = plc.read_area(area, 0, start, size)  # Read as bytes
                     if data_type == "INT":
                       value = int.from_bytes(value, byteorder='big')
                tag_data[tag_name] = {"address": f"{area}.{start}", "value": value}
            except Exception as e:
                print(f"Error reading tag {tag_name}: {e}")
                tag_data[tag_name] = {"address": f"{area}.{start}", "value": "Error"}

        plc.disconnect()
        print("Disconnected from PLC.")
        return tag_data

    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None

def main():
    plc_ip = find_plc_ip_address()

    if plc_ip:
        tag_information = collect_tags_and_values(plc_ip)

        if tag_information:
            print("\nCollected Tag Information:")
            for tag, data in tag_information.items():
                print(f"  Tag: {tag}, Address: {data['address']}, Value: {data['value']}")
        else:
            print("Failed to collect tag information.")
    else:
        print("Could not determine PLC IP address.")

if __name__ == "__main__":
    main()