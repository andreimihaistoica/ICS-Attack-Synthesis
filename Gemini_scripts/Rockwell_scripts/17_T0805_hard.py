import socket
import time
import subprocess

# Configuration - Consider making these configurable via arguments or a config file
SERIAL_CONVERTER_IP = "10.0.0.1"  #  Replace with the actual IP address of the serial to Ethernet converter
COM_PORT_BASE = 20001          # Base port number for the serial ports.  COM1 is assumed to be this.
NUM_PORTS_TO_BLOCK = 3         # Number of serial ports to block (COM1, COM2, COM3)

def get_plc_ip_address():
    """
    Attempts to discover the PLC's IP address.  This is a placeholder.
    In a real system, you'd need to use a proper discovery mechanism 
    (e.g., Rockwell's BootP utility, a network scan, or reading it from a configuration file).

    This example assumes the PLC is on the same subnet and responds to ping.
    It also makes assumptions about naming conventions.  **This is highly unlikely to work in a real environment without modification.**

    Returns:
        str: The PLC's IP address, or None if discovery fails.
    """
    try:
        # Placeholder:  Replace with a proper PLC discovery method.
        # This is just a very basic example and likely needs significant adjustments.
        result = subprocess.run(['ping', '-n', '1', 'PLC'], capture_output=True, text=True, timeout=5) # Assumes PLC hostname is 'PLC'
        if result.returncode == 0:
            # Extract IP from ping output (very fragile!)
            output_lines = result.stdout.splitlines()
            for line in output_lines:
                if "Reply from" in line:
                    parts = line.split()
                    plc_ip = parts[3]  # This is a brittle assumption.
                    return plc_ip
        else:
            print(f"Ping failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error discovering PLC IP: {e}")
        return None

def block_serial_com_ports(ip_address, port_base, num_ports):
    """
    Blocks specified serial COM ports by opening and holding TCP connections.
    """
    sockets = [] # Keep track of open sockets so we can close them properly on exit

    for i in range(num_ports):
        port = port_base + i
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5) # Set a timeout to prevent indefinite blocking on connection

            print(f"Attempting to connect to {ip_address}:{port}")
            sock.connect((ip_address, port))
            print(f"Successfully connected to {ip_address}:{port}. Holding connection open.")
            sockets.append(sock) # Store the socket

            # Optionally, send some data to keep the connection alive (e.g., null bytes)
            # sock.sendall(b'\x00')

        except socket.timeout:
            print(f"Connection to {ip_address}:{port} timed out.")
        except ConnectionRefusedError:
            print(f"Connection to {ip_address}:{port} refused.")
        except Exception as e:
            print(f"Error connecting to {ip_address}:{port}: {e}")

    print("Blocking serial COM ports... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(60)  # Hold connections open indefinitely (or until Ctrl+C)
            # Optionally, send keep-alive data periodically
            # for sock in sockets:
            #     try:
            #         sock.sendall(b'\x00')
            #     except:
            #         print("Socket Disconnected, exiting...")
            #         break
    except KeyboardInterrupt:
        print("\nStopping and closing connections...")
    finally:
        # Ensure all sockets are closed on exit, even if there's an error
        for sock in sockets:
            try:
                sock.close()
            except Exception as e:
                print(f"Error closing socket: {e}")
        print("Connections closed.")

if __name__ == "__main__":
    plc_ip = get_plc_ip_address()  #Attempt to find the PLC's IP
    if plc_ip:
        print(f"Found PLC IP Address: {plc_ip}")
    else:
        print("Failed to automatically discover PLC IP. Using configured Serial Converter IP.")
        plc_ip = SERIAL_CONVERTER_IP #Revert to configured value if discovery fails

    block_serial_com_ports(plc_ip, COM_PORT_BASE, NUM_PORTS_TO_BLOCK)