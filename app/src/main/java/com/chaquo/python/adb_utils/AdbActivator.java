package com.chaquo.python.adb_utils;

import static android.Manifest.permission.WRITE_SECURE_SETTINGS;

import android.content.ContentResolver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;

import androidx.annotation.RequiresApi;

import com.elvishew.xlog.Logger;
import com.elvishew.xlog.XLog;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class AdbActivator
{
    private final Logger logger = XLog.tag(this.getClass().getName()).build();
    private Context context = null;
    private AdbProcessManager adbProcess = null;

    public AdbActivator(Context context, String binaryDir, String adbBinaryPath)
    {
        this.context = context;
        this.adbProcess = new AdbProcessManager(binaryDir, adbBinaryPath);
    }

    // Pair device
    public boolean pairDevice(int pairingPort, String pairingCode) throws SecurityException
    {
        if (hasWriteSecureSettingsPermission()) {
            // This permission is only granted after pairing once.
            // So if this perm is granted, we can confirm that the pairing had been finished.
            logger.d("Device had been paired. Nothing to do here.");
            return true;
        }

        logger.d("Pairing device at port " + pairingPort + " with code " + pairingCode + "...");
        if(!adbProcess.pairDevice(pairingPort, pairingCode)) {
            logger.e("Fail to pair the device!");
            throw new SecurityException("Fail to pair the device");
        }
        logger.d("Pairing succeeded.");

        // After pairing, grant the WRITE_SECURE_SETTINGS permission for current app
        grantWriteSecureSettingsPermission();
        return true;
    }

    // Grant WRITE_SECURE_SETTINGS permission
    private void grantWriteSecureSettingsPermission() throws SecurityException {
        String appPackageName = context.getPackageName();
        logger.d("Granting permission WRITE_SECURE_SETTINGS for current app " + appPackageName);
        try {
            adbProcess.grantPermission(appPackageName, "android.permission.WRITE_SECURE_SETTINGS");
        } catch (AdbProcessManager.ExecException e) {
            logger.e(e.getMessage() + "\nStderr: " + e.getStderr());
            throw new SecurityException(e.getMessage() + "\nStderr: " + e.getStderr());
        }
        logger.d("Permission granted.");
    }

    // Check WRITE_SECURE_SETTINGS permission
    private boolean hasWriteSecureSettingsPermission() throws SecurityException {
        return context.checkSelfPermission(WRITE_SECURE_SETTINGS) == PackageManager.PERMISSION_GRANTED;
    }

    // Enable wireless ADB through secure settings
    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    protected void enableWirelessAdb() throws SecurityException
    {
        if(!hasWriteSecureSettingsPermission()) {
            logger.e("No permission for WRITE_SECURE_SETTINGS");
            throw new SecurityException("No permission for WRITE_SECURE_SETTINGS");
        }
        logger.d("WRITE_SECURE_SETTINGS permission granted.");

        logger.d("Enabling wireless ADB...");
        final ContentResolver cr = context.getContentResolver();
        Settings.Global.putInt(cr, "adb_wifi_enabled", 1);
        Settings.Global.putInt(cr, Settings.Global.ADB_ENABLED, 1);
        Settings.Global.putLong(cr, "adb_allowed_connection_time", 0L);

        if(Settings.Global.getInt(cr, "adb_wifi_enabled", 0) != 1) {
            logger.e("Fail to enable wireless ADB");
            throw new SecurityException("Fail to enable wireless ADB");
        }
        logger.d("Wireless ADB enabled.");
    }

    // Discover ADB service on current device with mDNS
    @RequiresApi(Build.VERSION_CODES.R)
    protected CompletableFuture<Integer> discoverAdbService()
    {
        final ContentResolver cr = context.getContentResolver();
        CompletableFuture<Integer> result = new CompletableFuture<>();
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(() -> {
            logger.d("Finding wireless ADB service...");
            final CountDownLatch latch = new CountDownLatch(1);
            AdbMdns adbMdns = new AdbMdns(context, AdbMdns.TLS_CONNECT, port -> {
                if (port <= 0) {
                    logger.e("Fail to find wireless ADB service.");
                    throw new SecurityException("Fail to find wireless ADB service");
                }
                logger.d("Wireless ADB service found at port " + port);
                result.complete(port);
                latch.countDown();
            });

            try {
                if (Settings.Global.getInt(cr, "adb_wifi_enabled", 0) == 1) {
                    logger.d("Wireless ADB mDNS finding...");
                    adbMdns.start();
                    latch.await(3, TimeUnit.SECONDS);
                    adbMdns.stop();
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });

        executor.shutdown();
        return result;
    }

    // Returns adb port number
    public CompletableFuture<Integer> enableAndDiscoverAdbPort() throws SecurityException, UnsupportedOperationException
    {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            enableWirelessAdb();
            return discoverAdbService();
        } else {
            throw new UnsupportedOperationException("Android version is too old");
        }
    }
}
