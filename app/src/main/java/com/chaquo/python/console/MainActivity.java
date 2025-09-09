package com.chaquo.python.console;

import android.app.*;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.system.ErrnoException;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.chaquo.python.PyObject;
import com.chaquo.python.adb_utils.AdbActivator;
import com.chaquo.python.utils.*;
import com.elvishew.xlog.LogLevel;
import com.elvishew.xlog.XLog;

import java.io.File;
import java.util.Map;
import java.util.concurrent.ExecutionException;

public class MainActivity extends PythonConsoleActivity {
    private static final int REQUEST_USB_DEBUG_PERMISSION = 1001;
    private static final String[] REQUIRED_PERMISSIONS = {
        "android.permission.WRITE_SECURE_SETTINGS"
    };
    
    // On API level 31 and higher, pressing Back in a launcher activity sends it to the back by
    // default, but that would make it difficult to restart the activity.
    @Override public void onBackPressed() {
        finish();
    }
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Check and request permissions on startup
        checkAndRequestPermissions();
    }
    
    private void checkAndRequestPermissions() {
        // Check if we have all required permissions
        boolean allPermissionsGranted = true;
        for (String permission : REQUIRED_PERMISSIONS) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                allPermissionsGranted = false;
                break;
            }
        }
        
        if (!allPermissionsGranted) {
            // Request permissions
            ActivityCompat.requestPermissions(this, REQUIRED_PERMISSIONS, REQUEST_USB_DEBUG_PERMISSION);
        } else {
            // All permissions already granted
        }
    }
    
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == REQUEST_USB_DEBUG_PERMISSION) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (allGranted) {
                // All permissions granted successfully
            } else {
                // Some permissions were denied
            }
        }
    }

    @Override protected Class<? extends Task> getTaskClass() {
        return Task.class;
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Start foreground service to keep MCP bridge alive
        Intent serviceIntent = new Intent(this, MCPBridgeService.class);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent);
        } else {
            startService(serviceIntent);
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // Service will continue running in background
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
            // Skip initial permission check - will be checked again after emulator detection
            
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
            
            // Check if running in emulator/Genymotion
            boolean isEmulator = android.os.Build.FINGERPRINT.startsWith("generic") ||
                                android.os.Build.FINGERPRINT.startsWith("unknown") ||
                                android.os.Build.MODEL.contains("google_sdk") ||
                                android.os.Build.MODEL.contains("Emulator") ||
                                android.os.Build.MODEL.contains("Android SDK built for x86") ||
                                android.os.Build.MANUFACTURER.contains("Genymotion") ||
                                android.os.Build.MANUFACTURER.contains("Genymobile") ||
                                android.os.Build.FINGERPRINT.contains("motion_phone") ||
                                (android.os.Build.BRAND.startsWith("generic") && android.os.Build.DEVICE.startsWith("generic")) ||
                                "google_sdk".equals(android.os.Build.PRODUCT) ||
                                android.os.Build.MODEL.contains("sdk_gphone") ||
                                android.os.Build.DEVICE.contains("emu") ||
                                android.os.Build.PRODUCT.contains("sdk_gphone");
            
            // Debug: Print device info
            print("Device info - FINGERPRINT: " + android.os.Build.FINGERPRINT);
            print("Device info - MODEL: " + android.os.Build.MODEL);
            print("Device info - MANUFACTURER: " + android.os.Build.MANUFACTURER);
            print("Device info - BRAND: " + android.os.Build.BRAND);
            print("Device info - DEVICE: " + android.os.Build.DEVICE);
            print("Device info - PRODUCT: " + android.os.Build.PRODUCT);
            print("Is emulator detected: " + isEmulator);
            
            // Re-check permissions with actual emulator status
            if (!checkPermissionsBeforeExecution(isEmulator)) {
                print("Required permissions not granted. Cannot proceed with ADB operations.");
                return;
            }
            
            if (isEmulator) {
                print("Running in emulator environment, using direct ADB connection...");
                // For emulator, use direct connection without wireless ADB pairing
                adbPort = 5555; // Default ADB port for emulator
                print("Using default emulator ADB port: " + adbPort);
            } else {
                try {
                    // Need to do wireless adb device pairing when the app is installed for the first time
                    // Once after the successful pairing, this line will be automatically skipped.
                    // ***** Enter the pairing port and pairing code here *****
                    adbActivator.pairDevice(6555, "924621");

                    // After pairing, ADB is auto connected to the device.
                    adbPort = adbActivator.enableAndDiscoverAdbPort().get();
                    print("Wireless ADB service found. ADB port: " + adbPort);
                } catch (SecurityException | ExecutionException | InterruptedException | UnsupportedOperationException e) {
                    print("Fail to attach to wireless ADB: " + e.getMessage());
                    return;
                }
            }

            // 3. Execute UiAutomator2 Python script
            print("About to execute Python script...");
            try (PyObject mainModule = py.getModule("main")) {
                print("Python module loaded successfully");
                // Call: load_android_configs(app, adb_dir, ld_dir, adb_port)
                print("Calling load_android_configs...");
                mainModule.callAttr("load_android_configs", getApplication(), adbExecutable.getAbsolutePath(), adbDir.getAbsolutePath(), adbPort);
                print("load_android_configs completed");
                // Call: main()
                print("Calling main()...");
                mainModule.callAttr("main");
                print("main() completed");
            } catch (Exception e) {
                print("Error executing Python script: " + e.getMessage());
                e.printStackTrace();
            }
        }
        
        private boolean checkPermissionsBeforeExecution(boolean isEmulator) {
            // Skip permission check for emulator environment
            if (isEmulator) {
                print("Running in emulator - skipping WRITE_SECURE_SETTINGS permission check");
                return true;
            }
            
            for (String permission : REQUIRED_PERMISSIONS) {
                if (ContextCompat.checkSelfPermission(getApplication(), permission) != PackageManager.PERMISSION_GRANTED) {
                    print("Permission denied: " + permission);
                    print("Required permissions not granted. Cannot proceed with ADB operations.");
                    return false;
                }
            }
            print("All required permissions verified. Proceeding with ADB operations...");
            return true;
        }
    }
}

