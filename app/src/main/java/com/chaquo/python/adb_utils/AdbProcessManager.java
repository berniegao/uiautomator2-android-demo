package com.chaquo.python.adb_utils;

import com.elvishew.xlog.Logger;
import com.elvishew.xlog.XLog;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

public class AdbProcessManager {
    private final Logger logger = XLog.tag(this.getClass().getName()).build();
    final private String binaryDir;
    final private String binaryPath;
    protected Process binaryProcess = null;

    public AdbProcessManager(String binaryDir, String binaryPath) {
        this.binaryDir = binaryDir;
        this.binaryPath = binaryPath;
    }

    // Start adb process with params
    public void start(List<String> params) throws RuntimeException {
        if(isAlive()) {
            kill();
        }
        List<String> cmd = new ArrayList<>(params);
        cmd.add(0, this.binaryPath);
        ProcessBuilder pb = new ProcessBuilder(cmd);
        Map<String, String> env = pb.environment();
        env.put("LD_LIBRARY_PATH", binaryDir);			// 设置 LD_LIBRARY_PATH

        try {
            binaryProcess = pb.start();
            logger.d("ADB process started. Cmd line: adb " + String.join(" ", params));
        }
        catch (IOException e) {
            logger.e("Failed to start ADB process! " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    // Kill the adb process
    public void kill() {
        if(isAlive()) {
            binaryProcess.destroyForcibly();
            logger.d("ADB process killed.");
        } else {
            logger.w("Failed to kill. ADB process is not running.");
        }
    }

    // Input text to process stdin
    public void writeStdin(String input) throws RuntimeException {
        if(!isAlive())
            throw new RuntimeException("ADB Process is not running");

        try (BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(binaryProcess.getOutputStream(), StandardCharsets.UTF_8))){
            bw.write(input);
            bw.flush();
            logger.d("Write stdin to ADB process: " + input);
        }
        catch (IOException e) {
            logger.e("Failed to write stdin of ADB process! " + e.getMessage());
            throw new RuntimeException(e);
        }
    }

    // Wait for the process to exit with timeout
    public ExecResult waitForExit(int timeout) throws RuntimeException {
        try {
            logger.d("Waiting for ADB process to exit...");

            // 标准输出和错误流并行读取，防止阻塞
            CompletableFuture<String> stdoutFuture = readStreamAsync(binaryProcess.getInputStream());
            CompletableFuture<String> stderrFuture = readStreamAsync(binaryProcess.getErrorStream());

            boolean finishInTime = binaryProcess.waitFor(timeout, TimeUnit.SECONDS);
            if (!finishInTime) {
                logger.e("Process timeout.");
                kill();
            }
            int exitCode = binaryProcess.exitValue();
            String stdout = stdoutFuture.get();
            String stderr = stderrFuture.get();
            logger.d("ADB Process exited with code " + exitCode);
            return new ExecResult(exitCode, stdout, stderr);
        }
        catch (InterruptedException | ExecutionException e) {
            throw new RuntimeException(e);
        }
        finally {
            // 如果发生任何错误，强行停止子进程
            if(isAlive()) {
                logger.e("Process timeout.");
                binaryProcess.destroyForcibly();
            }
            binaryProcess = null;
        }
    }

    // Wait for the process to exit
    public ExecResult waitForExit() throws RuntimeException {
        return waitForExit(300);           // Default timeout = 300s
    }

    // Get whether the process is running
    public boolean isAlive() { return binaryProcess != null && binaryProcess.isAlive(); }

    // Execute the ADB binary once and get the result
    public ExecResult execute(List<String> params, int timeout) throws RuntimeException{
        start(params);
        return waitForExit(timeout);
    }

    // Execute the ADB binary once and get the result
    public ExecResult execute(List<String> params) throws RuntimeException {
        return execute(params, 300);           // Default timeout = 300s
    }

    // Pair the device
    public boolean pairDevice(int pairingPort, String pairingCode) throws SecurityException, RuntimeException
    {
        this.start(List.of("pair", "127.0.0.1:" + String.valueOf(pairingPort)));
        this.writeStdin(pairingCode + "\n");
        ExecResult result = this.waitForExit();
        return result.getExitCode() == 0;
    }

    // Execute adb shell
    public ExecResult shell(List<String> params) {
        List<String> cmd = new ArrayList<>(params);
        cmd.add(0, "shell");
        return execute(cmd);
    }

    // Grant permission for app
    public boolean grantPermission(String appPackageName, String permissionName) throws ExecException{
        ExecResult result = shell(List.of("pm", "grant", appPackageName, permissionName));
        if(result.getExitCode() != 0)
            throw new ExecException("Fail to grant permission " + permissionName + " for " + appPackageName, result);
        return true;
    }

    public static class ExecResult {
        private final int exitCode;
        private final String stdout;
        private final String stderr;

        public ExecResult(int exitCode, String stdout, String stderr) {
            this.exitCode = exitCode;
            this.stdout = stdout;
            this.stderr = stderr;
        }

        public int getExitCode() { return exitCode; }
        public String getStdout() { return stdout; }
        public String getStderr() { return stderr; }
    }

    public static class ExecException extends Exception {
        private final ExecResult execResult;

        public ExecException(String message, ExecResult execResult) {
            super(message); // 通常message可以简要描述
            this.execResult = execResult;
        }

        public int getExitCode() { return execResult.getExitCode(); }
        public String getStdout() { return execResult.getStdout(); }
        public String getStderr() { return execResult.getStderr(); }
    }

    private String readStream(InputStream is) throws IOException {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
            String line;
            while ((line = br.readLine()) != null) {
                sb.append(line).append(System.lineSeparator());
            }
        }
        return sb.toString();
    }

    private CompletableFuture<String> readStreamAsync(InputStream is) {
        return CompletableFuture.supplyAsync(() -> {
            StringBuilder sb = new StringBuilder();
            try (BufferedReader br = new BufferedReader(new InputStreamReader(is))) {
                String line;
                while ((line = br.readLine()) != null) {
                    sb.append(line).append(System.lineSeparator());
                }
            } catch (IOException e) {
                throw new CompletionException(e);
            }
            return sb.toString();
        });
    }
}
