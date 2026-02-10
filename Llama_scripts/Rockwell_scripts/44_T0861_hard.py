from cpppo.server.enip import client
import socket
import time

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 44818))  # 44818 is the default port for EtherNet/IP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to collect point and tag values
def collect_point_tag_values():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the list of available tags
            tags = conn.read(['*'])
            print("Available tags:", tags)
            
            # Collect point and tag values
            point_tag_values = {}
            for tag in tags:
                value = conn.read([tag])
                point_tag_values[tag] = value
                print(f"{tag}: {value}")
            
            # Collect point and tag values for specific points
            specific_points = ['_IO_EM_DI_01', '_IO_EM_DI_02', '_IO_EM_DO_01', '_IO_EM_DO_02']
            specific_point_tag_values = {}
            for point in specific_points:
                value = conn.read([point])
                specific_point_tag_values[point] = value
                print(f"{point}: {value}")
    else:
        print("PLC IP address not found")

# Function to identify point and tag values
def identify_point_tag_values():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the list of available tags
            tags = conn.read(['*'])
            print("Available tags:", tags)
            
            # Identify point and tag values
            point_tag_identifiers = {}
            for tag in tags:
                identifier = conn.read([f"{tag}.Identifier"])
                point_tag_identifiers[tag] = identifier
                print(f"{tag}: {identifier}")
            
            # Identify point and tag values for specific points
            specific_points = ['_IO_EM_DI_01', '_IO_EM_DI_02', '_IO_EM_DO_01', '_IO_EM_DO_02']
            specific_point_tag_identifiers = {}
            for point in specific_points:
                identifier = conn.read([f"{point}.Identifier"])
                specific_point_tag_identifiers[point] = identifier
                print(f"{point}: {identifier}")
    else:
        print("PLC IP address not found")

# Main function to start the collection of point and tag values
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Collect point and tag values
        collect_point_tag_values()
        
        # Identify point and tag values
        identify_point_tag_values()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()