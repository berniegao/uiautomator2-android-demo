package com.chaquo.python.console;

import android.app.*;
import android.system.ErrnoException;

import com.chaquo.python.PyObject;
import com.chaquo.python.adb_utils.AdbActivator;
import com.chaquo.python.utils.*;
import com.elvishew.xlog.LogLevel;
import com.elvishew.xlog.XLog;

import java.io.File;
import java.util.Map;
import java.util.concurrent.ExecutionException;

public class MainActivity extends PythonConsoleActivity {
    // On API level 31 and higher, pressing Back in a launcher activity sends it to the back by
    // default, but that would make it difficult to restart the activity.
    @Override public void onBackPressed() {
        finish();
    }

    @Override protected Class<? extends Task> getTaskClass() {
        return Task.class;
    }

    public static class Task extends PythonConsoleActivity.Task
    {
        public Task(Application app) {
            super(app);
            XLog.init(LogLevel.ALL);
        }

        // Print to app console
        public void print(String text) {
            py.getModule("main").callAttr("print_to_console", text);
        }

        // This run() will be called in a background thread, no need to worry about ANR here
        @Override public void run()
        {
            // 1. Construct runtime environment in private directory for ADB binaries
            File adbDir = new File(getApplication().getFilesDir(), "adb");    // {PrivateDir}/adb/
            File adbExecutable = new File(adbDir, "adb");                     // {PrivateDir}/adb/adb (Executable)
            // Create symbolic links for ADB binaries
            try {
                new BinariesExporter(getApplication()).exportLinkTo(adbDir, Map.of(
                        "libz.so.1.3.1.so", "libz.so.1",
                        "libzstd.so.1.5.7.so", "libzstd.so.1",
                        "libadb.so", "adb"
                ));
            } catch (ErrnoException e) {
                print("Fail to create symbolic link: " + e.getMessage());
            }

            // 2. Pair device, enable wireless ADB service and find out ADB port number
            AdbActivator adbActivator = new AdbActivator(getApplication(), adbDir.getAbsolutePath(), adbExecutable.getAbsolutePath());
            int adbPort = 0;
            try {
                // Need to do wireless adb device pairing when the app is installed for the first time
                // Once after the successful pairing, this line will be automatically skipped.
                // ***** Enter the pairing port and pairing code here *****
                adbActivator.pairDevice(40007, "924621");

                // After pairing, ADB is auto connected to the device.
                adbPort = adbActivator.enableAndDiscoverAdbPort().get();
                print("Wireless ADB service found. ADB port: " + adbPort);
            } catch (SecurityException | ExecutionException | InterruptedException | UnsupportedOperationException e) {
                print("Fail to attach to wireless ADB: " + e.getMessage());
                return;
            }

            // 3. Execute UiAutomator2 Python script
            try (PyObject mainModule = py.getModule("main")) {
                // Call: load_android_configs(app, adb_dir, ld_dir, adb_port)
                mainModule.callAttr("load_android_configs", getApplication(), adbExecutable.getAbsolutePath(), adbDir.getAbsolutePath(), adbPort);
                // Call: main()
                mainModule.callAttr("main");
            } catch (Exception e) {
                print("Error executing Python script: " + e.getMessage());
            }
        }
    }
}
