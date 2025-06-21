import os
import sys

import uiautomator2

context = None
adb_address = ""

# Load configs from Android layor
def load_android_configs(app_context, adb_path: str, ld_dir: str, adb_port: int):
    global context
    context = app_context
    global adb_address
    adb_address = f"127.0.0.1:{adb_port}"

    os.environ["ADBUTILS_ADB_PATH"] = adb_path
    print("ADB Path set to:", adb_path)
    os.environ['LD_LIBRARY_PATH'] = ld_dir
    print("LD_LIBRARY_PATH set to:", ld_dir)

# Print something to python console
def print_to_console(text: str, end="\n"):
    print(text, end=end)


def main():
    print(f"Connecting to {adb_address}...")
    d = uiautomator2.connect(adb_address)
    print("Device has been connected. Device Info:")
    print(d.info)

    # Launch Bilibili APP
    d.app_start('tv.danmaku.bili', stop=True)
    d.wait_activity('.MainActivityV2')
    d(text="我的").wait(timeout=10)       # Wait for the splash AD to finish
    d(text="我的").click()

    # Show the fans count
    fans_count = d(resourceId="tv.danmaku.bili:id/fans_count").get_text()
    print(f"Fans count of my bilibili account: {fans_count}")
