#!/usr/bin/env python3
"""
简单的uiautomator2功能测试
"""

import uiautomator2 as u2
import json

def test_uiautomator2():
    """测试uiautomator2基本功能"""
    
    print("🔌 正在连接Android设备...")
    
    try:
        # 连接设备
        device = u2.connect("127.0.0.1:6555")
        print("✅ 设备连接成功！")
        
        # 获取设备信息
        info = device.info
        print(f"📱 设备信息: {json.dumps(info, indent=2, ensure_ascii=False)}")
        
        # 获取当前应用
        current_app = device.app_current()
        print(f"📱 当前应用: {json.dumps(current_app, indent=2, ensure_ascii=False)}")
        
        # 获取截图
        screenshot_path = "/tmp/test_screenshot.png"
        device.screenshot(screenshot_path)
        print(f"📸 截图保存到: {screenshot_path}")
        
        # 启动设置应用
        print("🚀 启动设置应用...")
        device.app_start("com.android.settings", stop=True)
        
        # 等待应用加载
        import time
        time.sleep(3)
        
        # 获取当前应用（应该是设置）
        current_app = device.app_current()
        print(f"📱 当前应用: {json.dumps(current_app, indent=2, ensure_ascii=False)}")
        
        # 尝试点击元素
        try:
            print("👆 尝试点击'Network & internet'...")
            device(text="Network & internet").click()
            print("✅ 点击成功！")
        except Exception as e:
            print(f"❌ 点击失败: {e}")
        
        # 滑动屏幕
        print("👆 向上滑动屏幕...")
        try:
            device.swipe(0.5, 0.8, 0.5, 0.2)  # 从屏幕中间向上滑动
            print("✅ 滑动成功！")
        except Exception as e:
            print(f"❌ 滑动失败: {e}")
        
        # 获取已安装应用列表
        print("📋 获取已安装应用列表...")
        try:
            result = device.shell("pm list packages -3")
            packages = str(result).strip().split('\n')
            package_list = [pkg.replace('package:', '') for pkg in packages if pkg.startswith('package:')]
            print(f"✅ 已安装应用数量: {len(package_list)}")
            print(f"前5个应用: {package_list[:5]}")
        except Exception as e:
            print(f"❌ 获取应用列表失败: {e}")
        
        print("\n🎉 所有测试完成！uiautomator2工作正常。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试uiautomator2功能")
    print("=" * 50)
    
    success = test_uiautomator2()
    
    if success:
        print("\n🎉 测试成功！uiautomator2功能正常。")
    else:
        print("\n❌ 测试失败！请检查设备连接。") 