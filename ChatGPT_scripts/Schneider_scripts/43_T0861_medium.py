from scapy.all import srp, Ether, ARP
from pymodbus.client.sync import ModbusTcpClient
import ipaddress

# Network scan parameters
NETWORK_CIDR = "192.168.1.0/24"  # Modify based on your subnet

def discover_plc_ip():
    """Scans the network to find the PLC's IP address by checking for Modbus TCP responses."""
    print("[*] Scanning for PLC...")
    
    # Generate IP Range
    hosts = [str(ip) for ip in ipaddress.IPv4Network(NETWORK_CIDR, strict=False)]
    
    # Send ARP request on network
    answered, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=hosts), timeout=2, verbose=False)
    
    for sent, received in answered:
        target_ip = received.psrc
        print(f"[+] Found potential device: {target_ip}")

        # Check if Modbus TCP (port 502) is open to identify PLC
        try:
            client = ModbusTcpClient(target_ip, port=502, timeout=2)
            if client.connect():
                print(f"[✔] PLC discovered at {target_ip}")
                client.close()
                return target_ip
        except:
            continue   # Not a Modbus device
    
    print("[!] No PLC found on the network.")
    return None

def collect_plc_data(plc_ip):
    """Retrieves tag values from the PLC via Modbus TCP."""
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip, port=502)

    if not client.connect():
        print("[X] Failed to connect to PLC")
        return
    
    print("[+] Connected to PLC, retrieving tag values...")

    # Read Inputs (Discrete Inputs - 0x02)
    inputs = client.read_discrete_inputs(0, 10, unit=1)
    print(f"[*] Discrete Inputs: {inputs.bits if inputs else 'Failed to read'}")

    # Read Coils (Outputs - 0x01)
    coils = client.read_coils(0, 10, unit=1)
    print(f"[*] Coils (Outputs): {coils.bits if coils else 'Failed to read'}")

    # Read Holding Registers (Internal Memory - 0x03)
    holding_registers = client.read_holding_registers(0, 10, unit=1)
    print(f"[*] Holding Registers: {holding_registers.registers if holding_registers else 'Failed to read'}")

    # Read Input Registers (Sensors/Data - 0x04)
    input_registers = client.read_input_registers(0, 10, unit=1)
    print(f"[*] Input Registers: {input_registers.registers if input_registers else 'Failed to read'}")

    client.close()
    print("[✔] Data collection complete.")

if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        collect_plc_data(plc_ip)
    else:
        print("[!] Unable to proceed without PLC IP.")