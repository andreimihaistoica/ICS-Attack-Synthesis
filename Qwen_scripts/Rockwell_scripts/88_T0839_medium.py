import requests
import hashlib
import os

# Configuration
PLC_IP = "192.168.1.100"
FIRMWARE_URL = "http://example.com/firmware/micro850_latest.bin"
FIRMWARE_CHECKSUM_URL = "http://example.com/firmware/micro850_latest.bin.sha256"

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def verify_checksum(file_path, expected_checksum):
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest() == expected_checksum

def update_firmware(plc_ip, firmware_path):
    # This is a placeholder for the actual firmware update command
    # You would need to use the appropriate command or API provided by Rockwell
    print(f"Updating firmware on PLC at {plc_ip} with {firmware_path}")
    # Example command (this will vary based on your setup)
    # os.system(f"plc_update_tool -i {plc_ip} -f {firmware_path}")

def main():
    # Download firmware
    firmware_path = download_file(FIRMWARE_URL, "micro850_latest.bin")
    
    # Download and verify checksum
    expected_checksum = requests.get(FIRMWARE_CHECKSUM_URL).text.strip()
    if not verify_checksum(firmware_path, expected_checksum):
        print("Firmware checksum verification failed. Aborting update.")
        return
    
    # Update firmware
    update_firmware(PLC_IP, firmware_path)
    print("Firmware update completed successfully.")

if __name__ == "__main__":
    main()