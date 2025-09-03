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
    
    # Use local network IP for gateway connection
    gateway_url = "http://192.168.2.53:8765"
    print(f"Using local network gateway URL: {gateway_url}")
    
    os.environ.setdefault("MCP_GATEWAY_WS_URL", gateway_url)
    os.environ.setdefault("MCP_GATEWAY_TOKEN", "devtoken")
    
    print(f"MCP Gateway URL: {os.environ['MCP_GATEWAY_WS_URL']}")
    print(f"MCP Gateway Token: {os.environ['MCP_GATEWAY_TOKEN']}")
    
    # Start MCP bridge in background
    start_reverse_mcp_from_env(adb_address)
    print("MCP bridge started in background thread")
