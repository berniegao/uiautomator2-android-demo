"""
Android UIAutomator2 MCP Server
基于Android内嵌uiautomator2的MCP服务器
"""

import logging
import json
import time
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
import uiautomator2 as u2

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/android-mcp.log')
    ]
)

# 创建MCP服务器实例
mcp = FastMCP("Android UIAutomator2 MCP Server")

# 全局设备实例
device = None
adb_address = "127.0.0.1:6555"  # Genymotion ADB地址

def init_device():
    """初始化设备连接"""
    global device
    try:
        device = u2.connect(adb_address)
        logging.info(f"Device connected: {device.info}")
        return True
    except Exception as e:
        logging.error(f"Failed to connect device: {e}")
        return False

# 初始化设备
if not init_device():
    logging.error("Failed to initialize device")

@mcp.tool("init_device")
def mcp_android_init_device(address: str = "127.0.0.1:5555") -> Dict[str, Any]:
    """初始化Android设备连接"""
    global device, adb_address
    try:
        adb_address = address
        device = u2.connect(adb_address)
        info = device.info
        logging.info(f"Device initialized: {info}")
        return {
            "success": True,
            "device_info": info,
            "address": adb_address
        }
    except Exception as e:
        logging.error(f"Failed to initialize device: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool("get_device_info")
def mcp_android_get_device_info() -> Dict[str, Any]:
    """获取设备信息"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        info = device.info
        return {
            "success": True,
            "device_info": info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool("get_screenshot")
def mcp_android_get_screenshot() -> str:
    """获取屏幕截图"""
    global device
    if not device:
        return "Device not initialized"
    
    try:
        screenshot_path = "/tmp/android_screenshot.png"
        device.screenshot(screenshot_path)
        return f"Screenshot saved to: {screenshot_path}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"

@mcp.tool("click_element")
def mcp_android_click_element(
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    xpath: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """点击界面元素"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        if text:
            device(text=text).click()
            return {"success": True, "method": "text", "target": text}
        elif resource_id:
            device(resourceId=resource_id).click()
            return {"success": True, "method": "resource_id", "target": resource_id}
        elif xpath:
            device.xpath(xpath).click()
            return {"success": True, "method": "xpath", "target": xpath}
        else:
            return {"error": "No selector provided"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("input_text")
def mcp_android_input_text(text: str, clear: bool = True) -> Dict[str, Any]:
    """输入文本"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        if clear:
            device.clear_text()
        device.send_keys(text)
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("swipe_screen")
def mcp_android_swipe_screen(
    direction: str = "up",
    scale: float = 0.9
) -> Dict[str, Any]:
    """滑动屏幕"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        if direction == "up":
            device.swipe_ext(scale, "up")
        elif direction == "down":
            device.swipe_ext(scale, "down")
        elif direction == "left":
            device.swipe_ext(scale, "left")
        elif direction == "right":
            device.swipe_ext(scale, "right")
        else:
            return {"error": "Invalid direction"}
        
        return {"success": True, "direction": direction, "scale": scale}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("start_app")
def mcp_android_start_app(package_name: str, stop: bool = True) -> Dict[str, Any]:
    """启动应用"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        device.app_start(package_name, stop=stop)
        return {"success": True, "package": package_name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("stop_app")
def mcp_android_stop_app(package_name: str) -> Dict[str, Any]:
    """停止应用"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        device.app_stop(package_name)
        return {"success": True, "package": package_name}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("get_current_app")
def mcp_android_get_current_app() -> Dict[str, Any]:
    """获取当前运行的应用信息"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        current_app = device.app_current()
        return {"success": True, "current_app": current_app}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("wait_element")
def mcp_android_wait_element(
    text: Optional[str] = None,
    resource_id: Optional[str] = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """等待元素出现"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        if text:
            element = device(text=text).wait(timeout=timeout)
        elif resource_id:
            element = device(resourceId=resource_id).wait(timeout=timeout)
        else:
            return {"error": "No selector provided"}
        
        if element:
            return {"success": True, "element_found": True}
        else:
            return {"success": False, "element_found": False}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("get_element_text")
def mcp_android_get_element_text(
    text: Optional[str] = None,
    resource_id: Optional[str] = None
) -> Dict[str, Any]:
    """获取元素文本"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        if text:
            element_text = device(text=text).get_text()
        elif resource_id:
            element_text = device(resourceId=resource_id).get_text()
        else:
            return {"error": "No selector provided"}
        
        return {"success": True, "text": element_text}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("execute_adb_command")
def mcp_android_execute_adb_command(command: str) -> Dict[str, Any]:
    """执行ADB命令"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        result = device.shell(command)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool("get_installed_packages")
def mcp_android_get_installed_packages() -> Dict[str, Any]:
    """获取已安装的应用包列表"""
    global device
    if not device:
        return {"error": "Device not initialized"}
    
    try:
        packages = device.shell("pm list packages -3").strip().split('\n')
        package_list = [pkg.replace('package:', '') for pkg in packages if pkg.startswith('package:')]
        return {"success": True, "packages": package_list}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # 启动MCP服务器
    mcp.run() 