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

            // 为ADB二进制构造运行环境
            File adbDir = new File(getApplication().getFilesDir(), "adb");    // 私有目录 /adb/
            File adbExecutable = new File(adbDir, "adb");        // 私有目录下的adb二进制文件
            extractADB(adbDir, adbExecutable);

            // 运行UiAutomator2脚本
            py.getModule("main").callAttr("load_android_configs", adbExecutable.getAbsolutePath(), adbDir.getAbsolutePath());
            py.getModule("main").callAttr("main");
        }

        @Override public void run() {
            py.getModule("main").callAttr("main");
        }

        // print到控制台
        private void print(String text) {
            py.getModule("main").callAttr("print_to_console", text);
        }

        // 为ADB创建符号链接
        private void extractADB(File adbDir, File adbExecutable){
            linkBinariesToDir(adbDir, Map.of(
                    "libz.so.1.3.1.so", "libz.so.1",
                    "libzstd.so.1.5.7.so", "libzstd.so.1",
                    "libadb.so", "adb"
            ));
        }

        // 当前平台下对应架构的 libxxx.so 将会被链接到 {linkingDir}/libxxx.so，注意linkingDir必须在应用私有目录下！
        // 如果fileNameMapping中有自定义名字映射，符号链接将创建为对应的设定好的文件名
        private void linkBinariesToDir(File linkingDir, Map<String, String> fileNameMapping) {
            if(linkingDir.exists())
                return;     // 目录已存在
            else
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
                        print("创建符号链接失败: " + e.getMessage());
                    }
                }
            }
        }
    }
}
