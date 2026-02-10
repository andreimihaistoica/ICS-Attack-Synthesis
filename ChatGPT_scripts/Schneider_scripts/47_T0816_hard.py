import time
from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient

def discover_plc(ip_range="192.168.9.0/24"):
    """
    Discover the PLC by performing an ARP scan within the provided IP range.
    Returns the IP address of the PLC if found.
    """
    print(f"Scanning for devices in the network range {ip_range}...")

    # ARP request broadcast within the range
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find devices
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # In this scenario, filter for the PLC's IP (if known parameters of PLC MAC vendor exist, include filters here)
    print("Discovered devices:")
    for device in devices:
        print(f"IP: {device['ip']}, MAC: {device['mac']}")

    # Return the PLC's IP (modify logic if you know it beforehand)
    # If static IP is provided as "192.168.9.24", we would validate and return that instead.
    for device in devices:
        if device['ip'] == "192.168.9.24":  # Add logic to identify your PLC
            print(f"PLC found at IP: {device['ip']}")
            return device['ip']

    print("No PLC found. Adjust IP range or check connection.")
    return None


def restart_plc(ip, modbus_port=502):
    """
    Connect to the PLC via Modbus TCP and send a restart command.
    """
    print(f"Connecting to PLC at IP {ip} on Modbus port {modbus_port}...")
    client = ModbusClient(host=ip, port=modbus_port, auto_open=True)

    if not client.open():
        print("Error: Unable to connect to PLC. Ensure the PLC is reachable.")
        return

    print("Connected to PLC. Sending shutdown/restart command...")
    
    # Check if a specific register for restart/shutdown exists.
    # For example: Writing to a control register using Modbus Function 5/6.
    # NOTE: The implementation depends on the target PLC's specific Modbus control logic.
    try:
        # Assuming the restart command is performed by writing a value (e.g., 1) to modbus register 0 (coil/register address).
        result = client.write_single_coil(0, True)

        if result:
            print("Shutdown/Restart command sent successfully.")
        else:
            print("Failed to send Shutdown/Restart command.")
    except Exception as e:
        print(f"An error occurred while sending the command: {e}")

    # Disconnect from the PLC
    client.close()


def main():
    # Step 1: Discover the PLC's IP address in the network.
    plc_ip = discover_plc(ip_range="192.168.9.0/24")  # Adjust the range based on your network

    if not plc_ip:
        print("Unable to locate the PLC. Exiting.")
        return

    # Step 2: Send a restart/shutdown command to the discovered PLC.
    restart_plc(plc_ip)


if __name__ == "__main__":
    main()