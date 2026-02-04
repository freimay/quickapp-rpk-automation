import subprocess
import time

# ================= 坐标与参数配置区 =================
# 1. 业务参数配置
# 此处输入包名
PACKAGE_NAME = "com.jieyuan.home" 
# 此处输入启动参数
LAUNCH_PARAMS = "/pages/Action?intent=2&IS_PREVIEW=1&TACTIC_TYPE=1&channelId=zll&TACTIC_ID=112&linkId=0204"
# 重新安装调试后，终端运行 adb shell dumpsys window | findstr mCurrentFocus 命令，拿到数据替换下面内容
DEBUGGER_MAIN = "org.hapjs.debugger/org.hapjs.debugger.HybridMainActivity"
FORBIDDEN_LOG = "开始上报" # 提审包断言关键词 

# 2. 物理坐标配置 (请在此填入您手动定位的 X Y 数值)
POS_SETTINGS_ICON = (1000, 180)      # 第一步：右上角设置齿轮
POS_UNSET_TEXT = (920, 740)         # 第二步：“未设置”文字所在行
POS_INPUT_FIELD = (0000, 0000)        # 第三步：进入设置后，参数输入框的中心
POS_SAVE_BTN = (980, 360)           # 第四步：右上角“保存”
POS_START_DEBUG_BTN = (700, 1300)    # 第五步：主界面“开始调试”按钮
POS_LOCAL_INSTALL_BTN = (540, 750)   # 首页“本地安装”蓝色图标的位置
POS_FIRST_FILE_ITEM = (810, 550)     # 点击文件管理
POS_INNER_ONE = (150, 550)     # 内部存储设备
POS_INNER_TWO = (150, 600)     # 测试 张驰文件夹

# 补充：输入法收起按钮 (您之前量到的 980, 1540)
POS_HIDE_KEYBOARD = (980, 1540) 
# =================================================

def run_adb(cmd):
    """编码安全的 ADB 调用"""
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', shell=True)

def input_text_fast(text):
    """合并指令的高效输入"""
    print(f"⌨️ 正在注入参数字符串...")
    safe_text = text.replace("&", r"\&").replace("?", r"\?").replace("=", r"\=")
    # 动作链：全选(Ctrl+A) -> 退格 -> 输入
    clear_and_input = (
        f'adb shell "input keyevent --metaState 28672 29 && '
        f'input keyevent 67 && '
        f'input text {safe_text}"'
    )
    run_adb(clear_and_input)

def start_pure_coordinate_workflow():
    print("="*50)
    print("🚀 快应用物理坐标自动化方案 V1.26")
    print("="*50)

    # 0. 环境清理
    run_adb("adb logcat -c")

    # 第一步：启动调试器
    print("[1/7] 正在拉起调试器...")
    run_adb(f"adb shell am start -n {DEBUGGER_MAIN}")
    time.sleep(2.5)

    # 第二步：点击右上角设置按钮
    print(f"[2/7] 点击设置图标 {POS_SETTINGS_ICON}...")
    run_adb(f"adb shell input tap {POS_SETTINGS_ICON[0]} {POS_SETTINGS_ICON[1]}")
    time.sleep(1.5)

    # 第三步：点击“未设置”进入参数页
    print(f"[3/7] 点击‘未设置’入口 {POS_UNSET_TEXT}...")
    run_adb(f"adb shell input tap {POS_UNSET_TEXT[0]} {POS_UNSET_TEXT[1]}")
    time.sleep(1.5)

    # 第四步：输入启动参数
    print(f"[4/7] 准备输入参数...")
    run_adb(f"adb shell input tap {POS_INPUT_FIELD[0]} {POS_INPUT_FIELD[1]}") # 获取焦点
    time.sleep(1.2) # 等待键盘弹出
    
    print("🧹 正在强制执行离散退格清空...")
    # 循环 80-100 次，根据你参数的长度决定
    for _ in range(160):
        # 每一条命令都是独立的 adb 进程，确保系统必须响应
        run_adb("adb shell input keyevent 67")
        # 如果还是太快，可以取消下面这一行的注释
        # time.sleep(0.01) 
    # -------------------------------------

    # 【收起键盘操作】
    run_adb(f"adb shell input tap {POS_HIDE_KEYBOARD[0]} {POS_HIDE_KEYBOARD[1]}")
    print("⏳ 等待 3 秒布局恢复...")
    time.sleep(3)    

    # # 【收起键盘操作】确保不挡住保存按钮
    # run_adb(f"adb shell input tap {POS_HIDE_KEYBOARD[0]} {POS_HIDE_KEYBOARD[1]}")
    # print("⏳ 等待 5 秒布局恢复...")
    # time.sleep(5)    

    input_text_fast(LAUNCH_PARAMS)
    time.sleep(1.5)

    # 第五步：点击保存
    print(f"[5/7] 点击‘保存’按钮 {POS_SAVE_BTN}...")
    run_adb(f"adb shell input tap {POS_SAVE_BTN[0]} {POS_SAVE_BTN[1]}")
    time.sleep(2.0)

    # 第六步：退回到主界面 (利用 am start 强制回到主页，最稳妥)
    print("[6/7] 强制返回主界面...")
    run_adb(f"adb shell am start -n {DEBUGGER_MAIN}")
    time.sleep(1.5)

    # 第七步：点击开始调试
    print(f"[7/7] 点击‘开始调试’ {POS_START_DEBUG_BTN}...")
    run_adb(f"adb shell input tap {POS_START_DEBUG_BTN[0]} {POS_START_DEBUG_BTN[1]}")

    # --- 后续：日志断言验证  ---
    print("\n🔍 正在进入市场模式合规性监测 (10秒)...")
    time.sleep(10)
    logs = run_adb("adb logcat -d -t 500").stdout
    if FORBIDDEN_LOG in logs:
        print(f"❌ [FAIL] 提审包检测到违规上报：{FORBIDDEN_LOG}") [cite: 1]
    else:
        print(f"✅ [PASS] 提审包合规，未发现违规上报。") [cite: 1]

if __name__ == "__main__":
    start_pure_coordinate_workflow()