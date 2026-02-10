import logging
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import hashlib

# Configure logging for capture and analysis
logging.basicConfig(filename="firmware_monitor.log", level=logging.INFO, format='%(asctime)s %(message)s')

# Step 1: Identify PLC IP address (Network Scanning)
def find_plc_ip(network_range="192.168.9.0/24"):
    logging.info("Scanning for devices on the network...")
    devices = []
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = srp(arp_request_broadcast, timeout=5, verbose=False)[0]

    for _, received in answered:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    for device in devices:
        logging.info(f"Found Device - IP: {device['ip']}, MAC: {device['mac']}")
    
    # Assuming the PLC IP is known to be in the specified network
    for device in devices:
        if device['ip'].startswith("192.168.9."):  # Example heuristic
            logging.info(f"PLC Identified at IP {device['ip']}")
            return device['ip']
    
    logging.warning("PLC not found on the network.")
    return None

# Step 2: Connect to PLC and retrieve firmware version
def retrieve_firmware_version(plc_ip):
    try:
        logging.info(f"Connecting to PLC at {plc_ip}...")
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            logging.error(f"Could not connect to PLC at {plc_ip}.")
            return None

        # Fetch firmware data: Assuming it's stored in a Modbus register
        # Replace with the actual register addresses specific to your device
        firmware_register_address = 0x00F0  # Example register for firmware version
        response = client.read_holding_registers(firmware_register_address, count=2)
        if response.isError():
            logging.error("Error fetching firmware data from PLC.")
            return None

        # Simulate extracting firmware version and checksum
        firmware_version = response.registers[0]
        firmware_checksum = response.registers[1]
        logging.info(f"Retrieved Firmware Version: {firmware_version}, Checksum: {firmware_checksum}")
        client.close()
        return firmware_version, firmware_checksum
    except Exception as e:
        logging.error(f"Error during PLC communication: {e}")
        return None

# Step 3: Validate firmware against known good version
def validate_firmware(firmware_version, firmware_checksum):
    # Known good firmware versions and their checksums (simulate a trusted database)
    known_firmwares = {
        102: "d41d8cd98f00b204e9800998ecf8427e",  # Example checksum
        103: "b6d81b360a5672d80c27430f39153e2c"
    }

    calculated_checksum = hashlib.md5(str(firmware_version).encode()).hexdigest()
    if firmware_version in known_firmwares:
        expected_checksum = known_firmwares[firmware_version]
        if calculated_checksum == expected_checksum:
            logging.info(f"Firmware version {firmware_version} is valid and untampered.")
            return True
        else:
            logging.warning(f"Firmware checksum mismatch for version {firmware_version}. Possible tampering detected!")
            return False
    else:
        logging.warning(f"Unknown firmware version {firmware_version}. Cannot validate.")
        return False

# Step 4: Main Execution
def main():
    network_range = "192.168.9.0/24"  # Assuming the PLC is in this subnet
    plc_ip = find_plc_ip(network_range)
    if plc_ip:
        firmware_data = retrieve_firmware_version(plc_ip)
        if firmware_data:
            firmware_version, firmware_checksum = firmware_data
            validate_firmware(firmware_version, firmware_checksum)
        else:
            logging.error("Failed to retrieve firmware data.")
    else:
        logging.error("No PLC detected on the network.")

if __name__ == "__main__":
    main()