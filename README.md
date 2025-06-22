# uiautomator2-android-demo

> Demo project for Python UiAutomator2 running in Android APP, with the support of chaquopy

一个简单的Demo，使Python [openatx/uiautomator2](https://github.com/openatx/uiautomator2) 框架可以在安卓APP中运行，并通过ADB连接本机执行操作，不再需要PC作为控制端。

使用 [chaquo/chaquopy-console](https://github.com/chaquo/chaquopy-console) 项目作为模板，并为UiAutomator2配置adb二进制及其依赖库的运行环境。

本项目仅作为概念验证，证明在 APP 中执行二进制 `adb` 并调试自身是完全可行的。实际场景建议重新编写APP，并参考此文的逻辑进行 `adb` 运行环境的配置，这样可以更灵活地实现所需要的业务逻辑和 APP 生命周期管理。

使用的版本号：

- Chaquopy 16.1.0
- Python 3.11
- ADB 1.0.41 Version 35.0.2-android-tools（提取自Termux）

## Overall Ideas

- 使用`Chaquopy`执行Python编写的`uiautomator2`脚本

- `uiautomator2`底层需要依赖ADB二进制程序进行工作，因此在APP中配置二进制程序的运行环境，让`uiautomator2`可以直接调用

- `uiautomator2`需要通过无线调试连接到本机，因此在APP中实现：

  - 自动启动无线调试
  - 配对设备
  - 通过mDNS服务发现本机无线调试的工作端口并传递给`uiautomator2`

  使`uiautomator2`无需人工干预，自动使用ADB连接到本机。

## Screenshots

<img src="docs/1.jpg" width="400" />

![](docs/2.png)

<img src="docs/3.jpg" width="500" />

## More Details

详见博客：[安卓 APP 内嵌 UiAutomator2 自动化框架实践 - YQ's Toy Box](https://blog.openyq.top/posts/35685/)
