from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import socket

def find_plc_on_network(timeout=2):
    """
    Scan for all devices in the local network and identify the Schneider Electric PLC
    by attempting a connection over the Modbus protocol.
    """
    print("[*] Scanning for PLC devices on the network...")

    # Define the local subnet (adjust according to your network settings)
    subnet = "192.168.9.0/24"
    # Create an ARP request to find all devices in the subnet
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet)
    response, _ = srp(request, timeout=timeout, verbose=0)  # Send the request

    # Store all found IPs in a list
    devices = []
    for sent, received in response:
        devices.append(received.psrc)  # 'psrc' is the IP address of the device

    print(f"[+] Found {len(devices)} devices.")
    print("[*] Checking which devices are running Modbus...")

    # Check for Modbus presence on each device
    for device in devices:
        try:
            client = ModbusTcpClient(device)
            if client.connect():
                print(f"[+] Found possible PLC at {device}")
                client.close()
                return device
        except Exception as e:
            continue

    print("[-] No suitable PLC found on the network.")
    return None


def change_plc_credentials(plc_ip, old_password, new_password):
    """
    Attempt to change the credentials on a PLC using Modbus requests.
    Note: Modbus does not natively support credential management. This part
    assumes a vendor-specific Modbus register can be written for this purpose.
    """
    print(f"[*] Connecting to PLC at {plc_ip}...")

    try:
        client = ModbusTcpClient(plc_ip)
        if not client.connect():
            print("[-] Unable to connect to the PLC.")
            return

        print("[+] Connected to the PLC.")

        # Assumed Modbus registers for credential management
        # (These registers are vendor-specific and NOT part of the Modbus standard)
        OLD_PASSWORD_REGISTER = 40001  # Example holding register for the old password
        NEW_PASSWORD_REGISTER = 40002  # Example holding register for the new password
        APPLIED_REGISTER = 40003       # Example to confirm the change

        # Write the old password to the OLD_PASSWORD_REGISTER
        print("[*] Sending old password...")
        old_pw_ascii = [ord(c) for c in old_password]  # Convert string to ASCII values
        client.write_registers(OLD_PASSWORD_REGISTER, old_pw_ascii)

        # Write the new password to the NEW_PASSWORD_REGISTER
        print("[*] Sending new password...")
        new_pw_ascii = [ord(c) for c in new_password]
        client.write_registers(NEW_PASSWORD_REGISTER, new_pw_ascii)

        # Apply the changes by writing a confirmation value (e.g., 1) to the APPLIED_REGISTER
        print("[*] Applying new password...")
        client.write_register(APPLIED_REGISTER, 1)

        print("[+] Credentials successfully changed!")
        client.close()

    except Exception as e:
        print(f"[-] Failed to change credentials: {e}")


def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = find_plc_on_network()
    if not plc_ip:
        return

    # Step 2: Change the PLC credentials
    old_password = "1234"  # Example old password. Adjust to the real one.
    new_password = "secureP@ssw0rd"  # Example new password
    change_plc_credentials(plc_ip, old_password, new_password)


if __name__ == "__main__":
    main()