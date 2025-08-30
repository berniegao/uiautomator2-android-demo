package com.chaquo.python.console;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;
import androidx.core.app.NotificationCompat;

public class MCPBridgeService extends Service {
    private static final String CHANNEL_ID = "MCPBridgeChannel";
    private static final int NOTIFICATION_ID = 1001;
    private static final String WAKE_LOCK_TAG = "MCPBridgeService::WakeLock";
    
    private PowerManager.WakeLock wakeLock;
    
    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        acquireWakeLock();
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Create and show notification
        Notification notification = createNotification();
        startForeground(NOTIFICATION_ID, notification);
        
        // Return START_STICKY to restart service if killed
        return START_STICKY;
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        releaseWakeLock();
    }
    
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "MCP Bridge Service",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Keeps MCP Bridge connection alive");
            channel.setShowBadge(false);
            
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }
    
    private Notification createNotification() {
        NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("MCP Bridge Active")
            .setContentText("Maintaining connection to gateway")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .setAutoCancel(false);
            
        return builder.build();
    }
    
    private void acquireWakeLock() {
        PowerManager powerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
        if (powerManager != null) {
            wakeLock = powerManager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                WAKE_LOCK_TAG
            );
            wakeLock.acquire();
        }
    }
    
    private void releaseWakeLock() {
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
            wakeLock = null;
        }
    }
} 