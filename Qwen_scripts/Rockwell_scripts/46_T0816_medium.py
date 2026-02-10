import subprocess
import pyodbc
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    print("Discovering PLC IP address...")
    # Run nmap to scan the network for devices
    nmap_output = subprocess.check_output(['nmap', '-p', '502', '--open', '192.168.1.0/24']).decode('utf-8')
    lines = nmap_output.split('\n')
    
    for line in lines:
        if "502/tcp open" in line:
            ip_address = line.split()[0]
            print(f"PLC IP address found: {ip_address}")
            return ip_address
    
    print("PLC IP address not found.")
    return None

# Function to connect to the PLC
def connect_to_plc(ip_address):
    print(f"Connecting to PLC at {ip_address}...")
    try:
        # Define the connection string for the PLC
        conn_str = f'DRIVER={{Rockwell Automation PLC Driver}};DEVICE={ip_address};PORT=502'
        conn = pyodbc.connect(conn_str)
        print("Connected to PLC.")
        return conn
    except pyodbc.Error as e:
        print(f"Failed to connect to PLC: {e}")
        return None

# Function to send the restart command to the PLC
def restart_plc(conn):
    print("Sending restart command to PLC...")
    try:
        # Define the command to restart the PLC
        cursor = conn.cursor()
        cursor.execute("RESTART")
        cursor.commit()
        print("Restart command sent successfully.")
    except pyodbc.Error as e:
        print(f"Failed to send restart command: {e}")

# Function to send the shutdown command to the PLC
def shutdown_plc(conn):
    print("Sending shutdown command to PLC...")
    try:
        # Define the command to shutdown the PLC
        cursor = conn.cursor()
        cursor.execute("SHUTDOWN")
        cursor.commit()
        print("Shutdown command sent successfully.")
    except pyodbc.Error as e:
        print(f"Failed to send shutdown command: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return

    # Connect to the PLC
    conn = connect_to_plc(plc_ip)
    if not conn:
        return

    # Choose the action (restart or shutdown)
    action = input("Enter 'restart' to restart the PLC or 'shutdown' to shut down the PLC: ").strip().lower()
    if action == 'restart':
        restart_plc(conn)
    elif action == 'shutdown':
        shutdown_plc(conn)
    else:
        print("Invalid action. Please enter 'restart' or 'shutdown'.")

    # Close the connection
    conn.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()