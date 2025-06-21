package com.chaquo.python.utils;

import android.app.Application;
import android.system.ErrnoException;
import android.system.Os;

import java.io.File;
import java.util.Map;

public class BinariesExporter {
    private final Application app;

    public BinariesExporter(Application app) {
        this.app = app;
    }

    // The libxxx.so for the architecture of the current platform will be linked to {linkingDir}/libxxx.so.
    //       (Note that the linkingDir must be in the application's private directory!)
    // If there is a custom name mapping in fileNameMapping, the symbolic link will be created to the corresponding file name.
    public void exportLinkTo(File linkingDir, Map<String, String> fileNameMapping) throws ErrnoException {
        if(linkingDir.exists())
            deleteDir(linkingDir);
        linkingDir.mkdirs();
        File nativeLibsFolder = new File(app.getApplicationInfo().nativeLibraryDir);
        File[] files = nativeLibsFolder.listFiles();
        if (files == null)
            return;
        for (File srcFile : files) {
            if (srcFile.isFile()) {
                String destName = srcFile.getName();
                if(fileNameMapping.containsKey(destName))
                    destName = fileNameMapping.get(destName);
                File linkFile = new File(linkingDir, destName);
                Os.symlink(srcFile.getAbsolutePath(), linkFile.getAbsolutePath());
            }
        }
    }

    private static boolean deleteDir(File f) {
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
