import socket
import telnetlib

# Step 1: Scan for the PLC's IP Address on the Local Subnet
def find_plc_ip(subnet_prefix, target_ip_suffix):
    print(f"Scanning for PLC in subnet {subnet_prefix}...")
    target_ip = f"{subnet_prefix}.{target_ip_suffix}"

    try:
        # Attempting to establish a connection to Modbus port 502 as an indicator of the PLC
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Timeout for scanning
        result = sock.connect_ex((target_ip, 502))

        # If the connection is successful, we assume the PLC is present
        if result == 0:
            print(f"PLC Found at IP Address: {target_ip}")
            sock.close()
            return target_ip
        else:
            print(f"No PLC detected at {target_ip}.")
            sock.close()
    except Exception as e:
        print(f"Error while checking {target_ip}: {str(e)}")
    return None


# Step 2: Block the Serial COM via Serial-to-Ethernet Converter
def block_serial_com(plc_ip, serial_port):
    print(f"Attempting to block Serial COM via TCP on IP {plc_ip}, Port {serial_port}...")
    try:
        # Open a Telnet session to hold connection to the serial port
        tn = telnetlib.Telnet(plc_ip, serial_port, timeout=5)
        print(f"Successfully opened TCP session on {plc_ip}:{serial_port}. The port is now blocked.")
        # Hold the session open indefinitely (or a suitable time for testing/demo purposes)
        print("Press Ctrl+C to exit and release the port...")
        tn.interact()  # Keep the session open to block the port
    except Exception as e:
        print(f"Failed to block Serial COM on {plc_ip}:{serial_port}. Error: {str(e)}")


# Main Execution
if __name__ == "__main__":
    # Define the subnet and PLC IP suffix based on the given scenario
    subnet_prefix = "192.168.9"  # Adjust based on your network configuration
    plc_ip_suffix = "24"         # From the prompt, the PLC's IP is 192.168.9.24
    serial_ports = [20001, 20002, 20003]  # Common ports for Serial-Ethernet converters

    # Step 1: Find PLC's IP Address
    plc_ip = find_plc_ip(subnet_prefix, plc_ip_suffix)

    if plc_ip:
        # Step 2: Block Serial COM on the desired serial-port-to-TCP mappings
        for port in serial_ports:
            block_serial_com(plc_ip, port)
    else:
        print("PLC not detected in the subnet. Aborting operation.")