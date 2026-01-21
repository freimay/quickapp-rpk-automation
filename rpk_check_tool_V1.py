import subprocess
import time
import re
import xml.etree.ElementTree as ET

# ================= 配置区域 =================
# 1. 目标启动参数 (确保包含您截图中的变量)
LAUNCH_PARAMS = "/pages/Action?intent=2&IS_PREVIEW=1&TACTIC_TYPE=1&channelId=zll&TACTIC_ID=112&linkId=0112"
# 2. 调试器主界面
DEBUGGER_MAIN = "org.hapjs.debugger/org.hapjs.debugger.MainActivity"
# 3. 断言关键词：提审包不应出现此内容
FORBIDDEN_LOG = "开始上报" 
# ===========================================

def run_adb(cmd):
    """编码安全的 ADB 调用，解决 Windows 环境下的 GBK/UTF-8 冲突"""
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
                coords = re.findall(r'\d+', node.get('bounds'))
                x1, y1, x2, y2 = map(int, coords)
                return (x1 + x2) // 2, (y1 + y2) // 2
    except: pass
    return None

def input_text_safe(text):
    """
    针对小米/Flyme 输入法优化的输入逻辑
    1. 使用原始字符串解决 Python 3.12 转义警告
    2. 使用双引号包裹 shell 指令，防止 & 符号截断
    """
    print(f"⌨️ 正在尝试填入参数...")
    # 修复 SyntaxWarning：在 Python 3.12 中使用原始字符串或双斜杠
    safe_text = text.replace("&", r"\&").replace("?", r"\?").replace("=", r"\=")
    
    # 核心修复：通过双引号包裹，强制 shell 将其视为一个整体字符串
    # 这样可以极大提高在第三方输入法环境下的落盘成功率
    run_adb(f'adb shell "input text {safe_text}"')

def check_reporting_logs():
    """提审包断言：监测是否有违规上报日志"""
    print("\n🔍 正在进入静默期日志监测 (10秒)...")
    time.sleep(10)
    # 获取最近 500 行日志
    recent_logs = run_adb("adb logcat -d -t 500").stdout
    if FORBIDDEN_LOG in recent_logs:
        print(f"❌ [FAIL] 提审包测试失败：检测到禁止的日志关键词 '{FORBIDDEN_LOG}'！")
    else:
        print(f"✅ [PASS] 提审包测试通过：未发现关键上报日志。")

def start_workflow():
    print("="*50)
    print("🚀 快应用调试器自动化工作流 (V1.18 稳定版)")
    print("="*50)

    # 0. 环境清理：清理旧日志
    run_adb("adb logcat -c")

    # 1. 启动调试器
    run_adb(f"adb shell am start -n {DEBUGGER_MAIN}")
    time.sleep(2)

    # 2. 点击右上角设置齿轮
    print("⚙️ 定位设置图标...")
    # 尝试通过位置点击 (针对您的小米手机坐标微调)
    run_adb("adb shell input tap 1000 170") 
    time.sleep(1.5)

    # 3. 点击“启动参数设置”
    print("📝 进入启动参数设置...")
    param_entry = get_element_coords({'text': '启动参数设置'})
    if param_entry:
        run_adb(f"adb shell input tap {param_entry[0]} {param_entry[1]}")
    else:
        run_adb("adb shell input tap 500 320") 
    time.sleep(1.5)

    # 4. 输入参数
    # 增加点击输入框动作，确保焦点
    run_adb("adb shell input tap 500 400")
    time.sleep(0.5)
    
    print("🧹 清空输入框...")
    for _ in range(80): # 增加退格次数确保清空
        run_adb("adb shell input keyevent 67")
    
    input_text_safe(LAUNCH_PARAMS)
    time.sleep(2)

    # 5. 保存
    print("💾 正在保存配置...")
    save_btn = get_element_coords({'text': '保存'})
    if save_btn:
        run_adb(f"adb shell input tap {save_btn[0]} {save_btn[1]}")
    else:
        # 截图显示保存位于右上角
        run_adb("adb shell input tap 980 150") 
    
    time.sleep(2)
    
    # 6. 拉起快应用并验证
    print("▶️ 点击“开始调试”按钮...")
    start_btn = get_element_coords({'text': '开始调试'})
    if start_btn:
        run_adb(f"adb shell input tap {start_btn[0]} {start_btn[1]}")
        # 执行提审包专项断言
        check_reporting_logs()
    else:
        print("❌ 未能回到主界面找到“开始调试”按钮")

if __name__ == "__main__":
    start_workflow()