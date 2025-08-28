# Android UIAutomator2 MCP Server

基于Android内嵌uiautomator2的MCP服务器，让AI助手能够直接控制Android设备进行自动化操作。

## 功能特性

### 设备管理
- 设备连接初始化
- 获取设备信息
- 屏幕截图

### UI自动化操作
- 元素点击（文本、资源ID、XPath）
- 文本输入
- 屏幕滑动
- 元素等待
- 获取元素文本

### 应用管理
- 应用启动/停止
- 获取当前运行应用
- 获取已安装应用列表

### 系统操作
- ADB命令执行
- 设备信息查询

## 安装和配置

### 1. 安装依赖

```bash
cd mcp_server
pip install -r requirements.txt
```

### 2. 配置MCP服务器

在Claude Desktop的配置目录下创建或编辑`mcp.json`文件：

**macOS**: `~/.cursor/mcp.json`
**Windows**: `%APPDATA%\Cursor\mcp.json`

```json
{
  "mcpServers": {
    "android-automation": {
      "command": "python",
      "args": [
        "/path/to/uiautomator2-android-demo/mcp_server/android_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/uiautomator2-android-demo/mcp_server",
        "ANDROID_HOME": "/opt/homebrew/share/android-commandlinetools"
      }
    }
  }
}
```

### 3. 确保Android设备连接

```bash
# 检查设备连接
adb devices

# 如果使用Genymotion，确保ADB端口正确
adb connect 127.0.0.1:6555
```

## 使用方法

配置完成后，你可以在Claude中直接使用所有可用的工具：

### 初始化设备
```python
# 初始化设备连接
await mcp.call_tool("mcp_android_init_device", {
    "address": "127.0.0.1:6555"
})
```

### 获取设备信息
```python
# 获取设备信息
await mcp.call_tool("mcp_android_get_device_info", {})
```

### 启动应用
```python
# 启动设置应用
await mcp.call_tool("mcp_android_start_app", {
    "package_name": "com.android.settings"
})
```

### 点击元素
```python
# 点击文本元素
await mcp.call_tool("mcp_android_click_element", {
    "text": "Network & internet"
})
```

### 输入文本
```python
# 输入文本
await mcp.call_tool("mcp_android_input_text", {
    "text": "Hello World",
    "clear": True
})
```

### 滑动屏幕
```python
# 向上滑动
await mcp.call_tool("mcp_android_swipe_screen", {
    "direction": "up",
    "scale": 0.9
})
```

### 获取截图
```python
# 获取屏幕截图
await mcp.call_tool("mcp_android_get_screenshot", {})
```

## 可用工具列表

| 工具名称 | 功能描述 |
|---------|---------|
| `init_device` | 初始化Android设备连接 |
| `get_device_info` | 获取设备信息 |
| `get_screenshot` | 获取屏幕截图 |
| `click_element` | 点击界面元素 |
| `input_text` | 输入文本 |
| `swipe_screen` | 滑动屏幕 |
| `start_app` | 启动应用 |
| `stop_app` | 停止应用 |
| `get_current_app` | 获取当前运行应用 |
| `wait_element` | 等待元素出现 |
| `get_element_text` | 获取元素文本 |
| `execute_adb_command` | 执行ADB命令 |
| `get_installed_packages` | 获取已安装应用列表 |

## 示例场景

### 场景1：自动打开飞行模式
```python
# 1. 启动设置应用
await mcp.call_tool("mcp_android_start_app", {
    "package_name": "com.android.settings"
})

# 2. 点击网络设置
await mcp.call_tool("mcp_android_click_element", {
    "text": "Network & internet"
})

# 3. 点击飞行模式
await mcp.call_tool("mcp_android_click_element", {
    "text": "Airplane mode"
})
```

### 场景2：自动化测试
```python
# 1. 启动测试应用
await mcp.call_tool("mcp_android_start_app", {
    "package_name": "com.example.testapp"
})

# 2. 等待登录按钮出现
await mcp.call_tool("mcp_android_wait_element", {
    "text": "登录",
    "timeout": 10
})

# 3. 点击登录按钮
await mcp.call_tool("mcp_android_click_element", {
    "text": "登录"
})

# 4. 输入用户名
await mcp.call_tool("mcp_android_input_text", {
    "text": "testuser"
})
```

## 故障排除

### 1. 设备连接失败
- 检查ADB设备连接：`adb devices`
- 确认设备IP和端口正确
- 检查防火墙设置

### 2. 元素找不到
- 使用截图功能查看当前界面
- 检查元素文本是否正确
- 尝试使用不同的定位方式

### 3. 权限问题
- 确保应用有必要的权限
- 检查ADB调试是否启用

## 开发

### 添加新工具
在`android_mcp_server.py`中添加新的`@mcp.tool`装饰器函数：

```python
@mcp.tool("new_tool_name")
def mcp_android_new_tool(param1: str, param2: int) -> Dict[str, Any]:
    """新工具的描述"""
    # 实现逻辑
    return {"success": True, "result": "操作结果"}
```

### 日志查看
日志文件位置：`/tmp/android-mcp.log`

## 许可证

MIT License 