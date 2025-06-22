package com.chaquo.python.adb_utils;

import android.annotation.SuppressLint;
import android.content.Context;
import android.net.nsd.NsdManager;
import android.net.nsd.NsdServiceInfo;
import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.lifecycle.Observer; // 或自定义callback

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.ServerSocket;
import java.util.Enumeration;

@RequiresApi(api = Build.VERSION_CODES.R)
public class AdbMdns {

    public static final String TLS_CONNECT = "_adb-tls-connect._tcp";
    public static final String TLS_PAIRING = "_adb-tls-pairing._tcp";
    public static final String TAG = "AdbMdns";

    private boolean registered = false;
    private boolean running = false;
    private String serviceName = null;
    private final DiscoveryListener listener;
    private final NsdManager nsdManager;
    private final Observer<Integer> observer;
    private final String serviceType;

    @SuppressLint("WrongConstant")
    public AdbMdns(@NonNull Context context, @NonNull String serviceType, @NonNull Observer<Integer> observer) {
        this.serviceType = serviceType;
        this.observer = observer;
        this.listener = new DiscoveryListener(this);
        this.nsdManager = (NsdManager) context.getSystemService(NsdManager.class);
    }

    public void start() {
        if (running) return;
        running = true;
        if (!registered) {
            nsdManager.discoverServices(serviceType, NsdManager.PROTOCOL_DNS_SD, listener);
        }
    }

    public void stop() {
        if (!running) return;
        running = false;
        if (registered) {
            nsdManager.stopServiceDiscovery(listener);
        }
    }

    private void onDiscoveryStart() {
        registered = true;
    }

    private void onDiscoveryStop() {
        registered = false;
    }

    private void onServiceFound(NsdServiceInfo info) {
        nsdManager.resolveService(info, new ResolveListener(this));
    }

    private void onServiceLost(NsdServiceInfo info) {
        if (info.getServiceName().equals(serviceName)) {
            observer.onChanged(-1);
        }
    }

    private void onServiceResolved(NsdServiceInfo resolvedService) {
        if (running && isSameNetwork(resolvedService) && isPortAvailable(resolvedService.getPort())) {
            serviceName = resolvedService.getServiceName();
            observer.onChanged(resolvedService.getPort());
        }
    }

    private boolean isSameNetwork(NsdServiceInfo resolvedService) {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface networkInterface = interfaces.nextElement();
                Enumeration<java.net.InetAddress> addresses = networkInterface.getInetAddresses();
                while (addresses.hasMoreElements()) {
                    java.net.InetAddress address = addresses.nextElement();
                    if (resolvedService.getHost().getHostAddress().equals(address.getHostAddress())) {
                        return true;
                    }
                }
            }
        } catch (Exception e) {
            // ignore
        }
        return false;
    }

    private boolean isPortAvailable(int port) {
        try (ServerSocket socket = new ServerSocket()) {
            socket.bind(new InetSocketAddress("127.0.0.1", port), 1);
            return false; // 可以绑定, 说明占用
        } catch (IOException e) {
            return true; // 绑定失败, 表示本地没被占用，本代码逻辑就是这么写的
        }
    }

    static class DiscoveryListener implements NsdManager.DiscoveryListener {
        private final AdbMdns adbMdns;

        DiscoveryListener(AdbMdns adbMdns) {
            this.adbMdns = adbMdns;
        }

        @Override
        public void onDiscoveryStarted(String serviceType) {
            Log.v(TAG, "onDiscoveryStarted: " + serviceType);
            adbMdns.onDiscoveryStart();
        }

        @Override
        public void onStartDiscoveryFailed(String serviceType, int errorCode) {
            Log.v(TAG, "onStartDiscoveryFailed: " + serviceType + ", " + errorCode);
        }

        @Override
        public void onDiscoveryStopped(String serviceType) {
            Log.v(TAG, "onDiscoveryStopped: " + serviceType);
            adbMdns.onDiscoveryStop();
        }

        @Override
        public void onStopDiscoveryFailed(String serviceType, int errorCode) {
            Log.v(TAG, "onStopDiscoveryFailed: " + serviceType + ", " + errorCode);
        }

        @Override
        public void onServiceFound(NsdServiceInfo serviceInfo) {
            Log.v(TAG, "onServiceFound: " + serviceInfo.getServiceName());
            adbMdns.onServiceFound(serviceInfo);
        }

        @Override
        public void onServiceLost(NsdServiceInfo serviceInfo) {
            Log.v(TAG, "onServiceLost: " + serviceInfo.getServiceName());
            adbMdns.onServiceLost(serviceInfo);
        }
    }

    static class ResolveListener implements NsdManager.ResolveListener {
        private final AdbMdns adbMdns;

        ResolveListener(AdbMdns adbMdns) {
            this.adbMdns = adbMdns;
        }

        @Override
        public void onResolveFailed(NsdServiceInfo nsdServiceInfo, int i) {
            // 可选：日志
        }

        @Override
        public void onServiceResolved(NsdServiceInfo nsdServiceInfo) {
            adbMdns.onServiceResolved(nsdServiceInfo);
        }
    }
}