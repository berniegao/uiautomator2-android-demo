package com.chaquo.python.utils;

import static android.Manifest.permission.WRITE_SECURE_SETTINGS;

import android.content.ContentResolver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;
import android.provider.Settings;

import androidx.annotation.RequiresApi;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class AdbActivator
{
    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    protected void enableWirelessAdb(Context context) throws SecurityException
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

    @RequiresApi(Build.VERSION_CODES.R)
    protected CompletableFuture<Integer> discoverAdbService(Context context)
    {
        final ContentResolver cr = context.getContentResolver();
        CompletableFuture<Integer> result = new CompletableFuture<>();
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.submit(() -> {
            final CountDownLatch latch = new CountDownLatch(1);
            AdbMdns adbMdns = new AdbMdns(context, AdbMdns.TLS_CONNECT, port -> {
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
    public CompletableFuture<Integer> enableAndDiscoverAdbPort(final Context context) throws SecurityException
    {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            enableWirelessAdb(context);
            return discoverAdbService(context);
        } else {
            throw new UnsupportedOperationException("Android version is too old");
        }
    }
}
