from pycomm3 import LogixDriver

def find_plc_ip():
    # In a real scenario, you might scan the network to find the PLC's IP address.
    # For simplicity, we'll assume the IP is known or provided.
    plc_ip = '192.168.1.100'  # Replace with the actual PLC IP address
    return plc_ip

def read_plc_data(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Read a tag from the PLC (replace 'MyTag' with an actual tag name)
            tag_value = plc.read('MyTag')
            print(f"Value of MyTag: {tag_value}")
    except Exception as e:
        print(f"Error reading PLC data: {e}")

def write_plc_data(plc_ip, tag_name, value):
    try:
        with LogixDriver(plc_ip) as plc:
            # Write a value to a tag in the PLC
            plc.write(tag_name, value)
            print(f"Successfully wrote {value} to {tag_name}")
    except Exception as e:
        print(f"Error writing PLC data: {e}")

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        read_plc_data(plc_ip)
        # Example: Write a value to a tag (use with caution)
        write_plc_data(plc_ip, 'MyTag', 42)
    else:
        print("PLC IP not found.")

if __name__ == "__main__":
    main()