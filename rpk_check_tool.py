import subprocess
import time
import re
import xml.etree.ElementTree as ET

# ================= 配置区域 =================
# 目标启动参数
LAUNCH_PARAMS = "/pages/Action?intent=2&IS_PREVIEW=1&TACTIC_TYPE=1&channelId=zll&TACTIC_ID=112&linkId=0112"
# 调试器主界面 Activity
DEBUGGER_MAIN = "org.hapjs.debugger/org.hapjs.debugger.MainActivity"
# ===========================================

def run_adb(cmd):
    """执行 ADB 命令"""
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', shell=True)

def get_element_coords(search_dict):
    """通过 XML 查找元素中心坐标"""
    run_adb("adb shell uiautomator dump /sdcard/view.xml")
    xml_content = run_adb("adb shell cat /sdcard/view.xml").stdout
    if not xml_content or "<node" not in xml_content:
        return None
    
    try:
        xml_content = xml_content[xml_content.find('<'):]
        root = ET.fromstring(xml_content)
        for node in root.iter():
            if all(node.get(k) == v for k, v in search_dict.items()):
                # 提取 bounds "[x1,y1][x2,y2]"
                coords = re.findall(r'\d+', node.get('bounds'))
                x1, y1, x2, y2 = map(int, coords)
                return (x1 + x2) // 2, (y1 + y2) // 2
    except Exception:
        pass
    return None

def input_text_safe(text):
    """安全输入带特殊字符的文本"""
    # ADB input text 不支持直接传输 & ? = 等字符，需要转义或使用广播
    # 这里通过转义处理
    safe_text = text.replace("&", r"\&").replace("?", r"\?").replace("=", r"\=")
    run_adb(f"adb shell input text {safe_text}")

def start_workflow():
    print("🚀 正在启动快应用调试器...")
    run_adb(f"adb shell am start -n {DEBUGGER_MAIN}")
    time.sleep(2)

    # 1. 点击右上角设置齿轮
    print("⚙️ 正在定位设置图标...")
    # 优先尝试通过 ID 查找 (快应用调试器常见设置 ID)
    settings_pos = get_element_coords({'resource-id': 'org.hapjs.debugger:id/menu_settings'})
    
    if not settings_pos:
        # 如果找不到 ID，根据截图位置，点击屏幕右上角 (通常横向 90% 纵向 5% 处)
        # 这里假设大部分 1080P 屏幕，坐标约 (980, 130)
        print("⚠️ 未找到 ID，尝试坐标点击...")
        settings_pos = (1000, 170) 

    run_adb(f"adb shell input tap {settings_pos[0]} {settings_pos[1]}")
    time.sleep(1.5)

    # 2. 点击“启动参数设置”
    print("📝 进入启动参数设置...")
    param_entry = get_element_coords({'text': '启动参数设置'})
    if param_entry:
        run_adb(f"adb shell input tap {param_entry[0]} {param_entry[1]}")
    else:
        # 兜底：如果文字识别失败，点击列表第一项位置
        run_adb("adb shell input tap 500 320") 
    time.sleep(1)

    # 3. 输入参数
    print("⌨️ 正在填入参数...")
    # 点击输入框中央
    run_adb("adb shell input tap 500 400")
    time.sleep(0.5)
    
    # 清空输入框（发送多次删除键）
    for _ in range(100):
        run_adb("adb shell input keyevent 67")
    
    input_text_safe(LAUNCH_PARAMS)
    time.sleep(1)

    # 4. 保存
    print("💾 正在保存...")
    save_btn = get_element_coords({'text': '保存'})
    if save_btn:
        run_adb(f"adb shell input tap {save_btn[0]} {save_btn[1]}")
        print("✅ 参数设置完成并保存！")
    else:
        # 截图显示保存位于右上角
        run_adb("adb shell input tap 950 150")
        print("⚠️ 尝试通过位置点击保存。")

if __name__ == "__main__":
    start_workflow()