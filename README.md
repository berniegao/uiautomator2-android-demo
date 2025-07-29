# uiautomator2-android-demo

> Demo project for Python UiAutomator2 running in Android APP, with the support of chaquopy

一个简单的Demo，**将 Python [uiautomator2](https://github.com/openatx/uiautomator2) 自动化脚本打包为APK**，无需PC控制端即可独立运行，并通过ADB连接本机执行操作，全程自动连接无需人工操作，设备不需要root权限。

使用 [chaquo/chaquopy-console](https://github.com/chaquo/chaquopy-console) 项目作为模板，并

- 为UiAutomator2配置adb二进制及其依赖库的运行环境
- 实现ADB无线调试设备配对、启动无线调试、服务发现并连接的全流程，整个过程完全自动执行
- 实际执行 uiautomator2 自动化脚本进行验证
- 后续还可以拓展脚本热更新等功能，非常简单

本项目仅作为概念验证，证明在 APP 中执行二进制 `adb` 并调试自身完全可行。实际场景建议参考此文的逻辑改写APP并进行 `adb` 运行环境的配置和ADB服务的自动连接，这样可以更灵活地实现所需要的业务逻辑和 APP 生命周期管理。

使用的版本号：

- Chaquopy 16.1.0
- Python 3.11
- ADB 1.0.41 Version 35.0.2-android-tools（提取自Termux）

## Advantages

- 使用chaquopy运行Python脚本，可以很方便地配置pip依赖库和脚本热更新
- 脚本完全自激活、自授权、脱机运行，直接通过APP安装运行，任何时候都不需要电脑等控制端，甚至第一次安装时都不需要
- 仅需APP第一次启动时，手动配对一下无线调试，以后每次启动都自动获取adb权限并执行脚本，全程无需人工干预
- 即使设备重启后仍然可以自动获取adb权限，重启不影响授权状态
- 脚本分发极其简单，直接分发编译后的APP到目标设备上，安装运行即可，无需任何额外配置
- 全开源方案，不依赖任何商业或闭源产品，项目自主可控，有利于二次开发

## Overall Ideas

- 使用`Chaquopy`执行Python编写的`uiautomator2`脚本
- `uiautomator2`底层需要依赖ADB二进制程序进行工作，因此要在APP中配置二进制程序的运行环境，并将adb二进制打包到APK中
- `uiautomator2`需要通过无线调试连接到本机，因此需要在APP中实现如下自动化流程：
  - 自动启动无线调试
  - 配对设备
  - 通过mDNS服务发现本机无线调试的工作端口并传递给`uiautomator2`
- APP调整无线调试相关设置需要系统内部权限`WRITE_SECURE_SETTINGS`，因此在第一次设备配对完成后，APP自动使用`adb shell pm grant`为自身授予相关权限

## Screenshots

<img src="docs/1.jpg" width="400" />

![](docs/2.png)

<img src="docs/3.jpg" width="500" />

## More Details

详见博客：[Python UiAutomator2 框架打包 APK 实战 - YQ's Toy Box](https://blog.openyq.top/posts/35685/)
