import snap7

# Define the IP address of the PLC (replace with the actual IP address)
plc_ip_address = "192.168.0.2"

# Create a client object
client = snap7.S7Client()

# Connect to the PLC
client.Connect(plc_ip_address, 0, 1)

# Check if the connection is successful
if client.Connected():
    print("Connected to the PLC")
else:
    print("Failed to connect to the PLC")

# Define the new IP address
new_ip_address = "192.168.0.22"

# Define the hardware configuration
hw_config = {
    "IP Address": new_ip_address,
    "Subnet Mask": "255.255.255.0",
    "Gateway": "192.168.0.1"
}

# Download the hardware configuration to the PLC
client.DownloadHWConfig(hw_config)

# Check if the download is successful
if client.DownloadHWConfig(hw_config):
    print("Hardware configuration downloaded successfully")
else:
    print("Failed to download hardware configuration")

# Disconnect from the PLC
client.Disconnect()