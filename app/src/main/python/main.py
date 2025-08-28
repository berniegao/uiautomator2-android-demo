import os
import sys
import warnings

import uiautomator2
import asyncio
from reverse_mcp_bridge import start_reverse_mcp_from_env

warnings.filterwarnings("ignore", category=ResourceWarning)

context = None
adb_address = ""

# Load configs from Android layor
def load_android_configs(app_context, adb_path: str, ld_dir: str, adb_port: int):
    global context
    context = app_context
    global adb_address
    adb_address = f"127.0.0.1:{adb_port}"

    print("")
    os.environ["ADBUTILS_ADB_PATH"] = adb_path
    print(f"ADB Path set to: {adb_path}")
    os.environ['LD_LIBRARY_PATH'] = ld_dir
    print(f"LD_LIBRARY_PATH set to:{ld_dir}\n")

# Print something to python console
def print_to_console(text: str, end="\n"):
    print(text, end=end)


def main():
    print(f"Connecting to {adb_address}...\n")
    d = uiautomator2.connect(adb_address)
    print(f"Device has been connected. Device Info: {d.info}\n")

    # Start reverse MCP bridge in background
    print("Starting MCP bridge connection...")
    
    # Use 127.0.0.1 for adb reverse
    gateway_url = "http://127.0.0.1:8765"
    print(f"Using adb reverse gateway URL: {gateway_url}")
    
    os.environ.setdefault("MCP_GATEWAY_WS_URL", gateway_url)
    os.environ.setdefault("MCP_GATEWAY_TOKEN", "devtoken")
    
    print(f"MCP Gateway URL: {os.environ['MCP_GATEWAY_WS_URL']}")
    print(f"MCP Gateway Token: {os.environ['MCP_GATEWAY_TOKEN']}")
    
    # Start MCP bridge in background
    start_reverse_mcp_from_env(adb_address)
    print("MCP bridge started in background thread")

    try:
        # Launch Settings APP
        print("Starting Settings APP...")
        d.app_start('com.android.settings', stop=True)
        print("Settings APP started successfully")
        
        # Wait for main activity
        print("Waiting for main activity...")
        d.wait_activity('.Settings', timeout=30)
        print("Settings activity loaded")
        
        # Wait a bit for the app to fully load
        import time
        time.sleep(3)
        
        # Show current page info
        print("Current page info:", d.app_current())
        
        # Keep the app running for MCP bridge to work
        print("Keeping app running for MCP bridge...")
        while True:
            time.sleep(10)
            print("App still running, MCP bridge active...")
            
    except Exception as e:
        print(f"Error in main execution: {e}")
        print("Current app info:", d.app_current())
