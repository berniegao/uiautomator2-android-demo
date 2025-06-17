import os
import uiautomator2

from android.widget import Toast

context = None

# Load configs from Android layor
def load_android_configs(app_context, adb_path: str, ld_dir: str):
    global context
    context = app_context
    os.environ["ADBUTILS_ADB_PATH"] = adb_path
    print("ADB Path set to:", adb_path)
    os.environ['LD_LIBRARY_PATH'] = ld_dir
    print("LD_LIBRARY_PATH set to:", ld_dir)

# Make a toast of Android APP
def make_toast(text: str, is_long_toast: bool = False):
    toast = Toast.makeText(context, text, Toast.LENGTH_LONG if is_long_toast else Toast.LENGTH_SHORT)
    toast.show()


def main():
    d = uiautomator2.connect()
    print("Device has been connected. Device Info:")
    print(d.info)

    d.app_start('tv.danmaku.bili', stop=True)   # Launch Bilibili APP
    d.wait_activity('.MainActivityV2')
    d.sleep(7)                  # Wait for the splash AD to finish
    d(text="我的").click()

    # Show the fans count
    fans_count = d(resourceId="tv.danmaku.bili:id/fans_count").get_text()
    print(f"Fans count of my bilibili account: {fans_count}")
    make_toast(f"Fans count of my bilibili account: {fans_count}", is_long_toast=True)
