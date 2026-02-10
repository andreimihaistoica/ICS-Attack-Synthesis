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

# Function to collect the I/O Image
def collect_io_image():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Read the input image table
            input_image_table = conn.read(['Input_Image_Table'])
            print("Input Image Table:", input_image_table)
            
            # Read the output image table
            output_image_table = conn.read(['Output_Image_Table'])
            print("Output Image Table:", output_image_table)
            
            # Read the I/O Image state
            io_image_state = conn.read(['IO_Image_State'])
            print("I/O Image State:", io_image_state)
            
            # Collect the I/O Image state of specific inputs and outputs
            io_image_state_specific = {}
            for tag in ['_IO_EM_DI_01', '_IO_EM_DI_02', '_IO_EM_DO_01', '_IO_EM_DO_02']:
                value = conn.read([tag])
                io_image_state_specific[tag] = value
                print(f"{tag}: {value}")
    else:
        print("PLC IP address not found")

# Function to use Native API to access the memory regions directly
def use_native_api():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Create an EtherNet/IP client
        with client.connector(host=plc_ip) as conn:
            # Use Native API to access the memory regions directly
            # This step is highly dependent on the specific API and implementation
            # For simplicity, let's assume we have a Native API library
            import native_api
            native_api_client = native_api.Client(plc_ip)
            native_api_client.connect()
            
            # Read the I/O Image state using Native API
            io_image_state_native_api = native_api_client.read_io_image_state()
            print("I/O Image State (Native API):", io_image_state_native_api)
            
            native_api_client.disconnect()
    else:
        print("PLC IP address not found")

# Main function to start the collection of I/O Image
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Collect the I/O Image
        collect_io_image()
        
        # Use Native API to access the memory regions directly
        use_native_api()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()