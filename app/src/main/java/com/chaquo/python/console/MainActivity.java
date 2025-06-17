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

    public static class Task extends PythonConsoleActivity.Task {
        public Task(Application app) {
            super(app);
        }

        @Override public void run() {
            // Construct runtime environment in private directory for ADB binaries
            File adbDir = new File(getApplication().getFilesDir(), "adb");    // {PrivateDir}/adb/
            File adbExecutable = new File(adbDir, "adb");                     // {PrivateDir}/adb/adb (Executable)
            extractADB(adbDir, adbExecutable);

            // Execute UiAutomator2 Python script
            // Call: load_android_configs(app, adb_dir, ld_dir)
            py.getModule("main")
                    .callAttr("load_android_configs", getApplication(), adbExecutable.getAbsolutePath(), adbDir.getAbsolutePath());
            // Call: main()
            py.getModule("main").callAttr("main");
        }

        // Print to app console
        public void print(String text) {
            py.getModule("main").callAttr("print_to_console", text);
        }

        // Create symbolic links for ADB binaries
        private void extractADB(File adbDir, File adbExecutable){
            linkBinariesToDir(adbDir, Map.of(
                    "libz.so.1.3.1.so", "libz.so.1",
                    "libzstd.so.1.5.7.so", "libzstd.so.1",
                    "libadb.so", "adb"
            ));
        }

        // The libxxx.so for the architecture of the current platform will be linked to {linkingDir}/libxxx.so.
        //       (Note that the linkingDir must be in the application's private directory!)
        // If there is a custom name mapping in fileNameMapping, the symbolic link will be created to the corresponding file name.
        private void linkBinariesToDir(File linkingDir, Map<String, String> fileNameMapping) {
            if(linkingDir.exists())
                deleteDir(linkingDir);
            linkingDir.mkdirs();
            File nativeLibsFolder = new File(getApplication().getApplicationInfo().nativeLibraryDir);
            File[] files = nativeLibsFolder.listFiles();
            if (files == null)
                return;
            for (File srcFile : files) {
                if (srcFile.isFile()) {
                    String destName = srcFile.getName();
                    if(fileNameMapping.containsKey(destName))
                        destName = fileNameMapping.get(destName);
                    File linkFile = new File(linkingDir, destName);
                    try {
                        Os.symlink(srcFile.getAbsolutePath(), linkFile.getAbsolutePath());
                    } catch (ErrnoException e) {
                        print("Fail to create symbolic link: " + e.getMessage());
                    }
                }
            }
        }

        public static boolean deleteDir(File f) {
            if(f == null)
                return true;
            if (f.isDirectory()) {
                String[] children = f.list();
                if (children != null) {
                    for (String child : children) {
                        boolean success = deleteDir(new File(f, child));
                        if (!success) {
                            return false;
                        }
                    }
                }
            }
            return f.delete();
        }
    }
}
