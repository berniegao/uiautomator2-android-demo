package com.chaquo.python.console;

import android.app.*;
import android.system.ErrnoException;
import android.system.Os;

import com.chaquo.python.utils.*;

import java.io.File;
import java.util.Map;

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
        }

        // Print to app console
        public void print(String text) {
            py.getModule("main").callAttr("print_to_console", text);
        }

        @Override public void run() {
            // Construct runtime environment in private directory for ADB binaries
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

            // Execute UiAutomator2 Python script
            // Call: load_android_configs(app, adb_dir, ld_dir)
            py.getModule("main").callAttr("load_android_configs", getApplication(), adbExecutable.getAbsolutePath(), adbDir.getAbsolutePath());
            // Call: main()
            py.getModule("main").callAttr("main");
        }
    }
}
