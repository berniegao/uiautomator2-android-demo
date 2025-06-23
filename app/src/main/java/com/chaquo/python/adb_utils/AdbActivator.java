package com.chaquo.python.adb_utils;

import static android.Manifest.permission.WRITE_SECURE_SETTINGS;

import android.content.ContentResolver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;

import androidx.annotation.RequiresApi;

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
        if(!adbProcess.pairDevice(pairingPort, pairingCode))
            throw new SecurityException("Fail to pair the device");

        // After pairing, grant the WRITE_SECURE_SETTINGS permission for current app
        try {
            String appPackageName = context.getPackageName();
            adbProcess.grantPermission(appPackageName, "WRITE_SECURE_SETTINGS");
        } catch (AdbProcessManager.ExecException e) {
            throw new SecurityException(e.getMessage() + "\nStderr: " + e.getStderr());
        }
        return true;
    }

    // Enable wireless ADB through secure settings
    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    protected void enableWirelessAdb() throws SecurityException
    {
        if(context.checkSelfPermission(WRITE_SECURE_SETTINGS) != PackageManager.PERMISSION_GRANTED)
            throw new SecurityException("No permission for WRITE_SECURE_SETTINGS");

        final ContentResolver cr = context.getContentResolver();
        Settings.Global.putInt(cr, "adb_wifi_enabled", 1);
        Settings.Global.putInt(cr, Settings.Global.ADB_ENABLED, 1);
        Settings.Global.putLong(cr, "adb_allowed_connection_time", 0L);

        if(Settings.Global.getInt(cr, "adb_wifi_enabled", 0) != 1)
            throw new SecurityException("Fail to enable wireless ADB");
    }

    // Discover ADB service on current device with mDNS
    @RequiresApi(Build.VERSION_CODES.R)
    protected CompletableFuture<Integer> discoverAdbService()
    {
        final ContentResolver cr = context.getContentResolver();
        CompletableFuture<Integer> result = new CompletableFuture<>();
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(() -> {
            final CountDownLatch latch = new CountDownLatch(1);
            AdbMdns adbMdns = new AdbMdns(context, AdbMdns.TLS_CONNECT, port -> {
                if (port <= 0)
                    throw new SecurityException("Fail to enable wireless ADB");
                result.complete(port);
                latch.countDown();
            });

            try {
                if (Settings.Global.getInt(cr, "adb_wifi_enabled", 0) == 1) {
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
