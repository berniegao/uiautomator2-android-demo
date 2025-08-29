# UIAutomator MCP Server

这是一个基于MCP (Model Context Protocol) 的Android自动化服务器，它通过网关将请求转发到Android设备。

## 功能特性

- **MCP协议支持**: 完全兼容MCP协议
- **Android自动化**: 支持启动应用、获取设备信息等操作
- **网关集成**: 通过Socket.IO网关与Android设备通信
- **异步处理**: 支持异步RPC调用

## 可用工具

### 1. start_app
启动Android应用程序

**参数:**
- `package_name` (string, 必需): 要启动的应用包名
- `stop` (boolean, 可选): 是否在启动前停止应用，默认为true

**示例:**
```json
{
  "package_name": "com.android.settings",
  "stop": true
}
```

### 2. get_device_info
获取Android设备信息

**参数:** 无

**返回信息包括:**
- 当前应用包名
- 屏幕尺寸和分辨率
- 设备型号
- Android版本
- 屏幕状态等

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确保网关运行
```bash
# 启动网关
nohup bash -c 'GATEWAY_TOKEN=devtoken python3 gateway_stub.py' > gateway.log 2>&1 &
```

### 3. 配置MCP客户端
将 `mcp_config.json` 添加到你的MCP客户端配置中：

```json
{
  "mcpServers": {
    "uiautomator": {
      "command": "python3",
      "args": [
        "uiautomator_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": ".",
        "GATEWAY_TOKEN": "devtoken"
      }
    }
  }
}
```

## 使用方法

### 1. 直接运行测试
```bash
python3 test_mcp_server.py
```

### 2. 作为MCP服务器运行
```bash
python3 uiautomator_mcp_server.py
```

### 3. 通过MCP客户端使用
配置好MCP客户端后，你可以使用以下工具：

- `start_app`: 启动Android应用
- `get_device_info`: 获取设备信息

## 架构说明

```
MCP Client → UIAutomator MCP Server → Gateway → Android Device
```

1. **MCP Client**: 发送MCP工具调用请求
2. **UIAutomator MCP Server**: 接收MCP请求，转换为RPC调用
3. **Gateway**: 转发RPC调用到Android设备
4. **Android Device**: 执行实际的操作并返回结果

## 日志和调试

- MCP Server日志: 控制台输出
- Gateway日志: `gateway.log` 文件
- 连接状态: 通过日志查看设备和客户端连接情况

## 故障排除

### 1. 连接问题
- 确保网关正在运行 (`ps aux | grep gateway_stub`)
- 检查端口8765是否被占用 (`lsof -i :8765`)
- 验证GATEWAY_TOKEN配置

### 2. 设备连接问题
- 确保Android设备已连接 (`adb devices`)
- 检查设备是否支持uiautomator2

### 3. MCP协议问题
- 验证MCP客户端配置
- 检查工具参数格式

## 扩展功能

可以通过以下方式扩展功能：

1. **添加新工具**: 在 `UIAutomatorMCPServer` 类中添加新的工具装饰器
2. **增强RPC调用**: 修改 `send_rpc_call` 方法以支持更复杂的交互
3. **添加认证**: 实现更安全的认证机制
4. **支持多设备**: 扩展以支持多个Android设备

## 许可证

本项目遵循MIT许可证。 