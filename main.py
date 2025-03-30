"""
Django Tenants ToolBox - 主入口點

這是一個用於 Django 多租戶應用開發的工具箱，
幫助開發者更輕鬆地管理多租戶項目。
"""

import os
import sys
import subprocess
import tempfile
import threading
import time
from pathlib import Path
import re

# 確保 tkinter 正確導入
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# 檢查是否是打包後的 EXE
if getattr(sys, "frozen", False):
    # 如果是打包後的 EXE
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是直接執行 Python 腳本
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 全局變數
PROJECT_DIR = None
VENV_DIR = None
VENV_PYTHON = None
VENV_ACTIVATE = None
ENV_FILE = None
ENV_VARS = {}


def find_manage_py(start_dir):
    """從給定目錄開始，尋找 manage.py 文件"""
    # 首先檢查當前目錄
    if os.path.exists(os.path.join(start_dir, "manage.py")):
        return start_dir

    # 檢查直接子目錄
    try:
        for item in os.listdir(start_dir):
            item_path = os.path.join(start_dir, item)
            if os.path.isdir(item_path) and os.path.exists(
                os.path.join(item_path, "manage.py")
            ):
                return item_path
    except PermissionError:
        # 無法列出目錄內容，忽略
        pass
    except OSError:
        # 其他OS錯誤，忽略
        pass

    # 檢查當前工作目錄
    current_dir = os.getcwd()
    if current_dir != start_dir and os.path.exists(
        os.path.join(current_dir, "manage.py")
    ):
        return current_dir

    # 檢查上級目錄
    try:
        parent_dir = os.path.dirname(start_dir)
        if parent_dir != start_dir and os.path.exists(
            os.path.join(parent_dir, "manage.py")
        ):
            return parent_dir

        # 檢查上級目錄的子目錄
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if (
                item_path != start_dir
                and os.path.isdir(item_path)
                and os.path.exists(os.path.join(item_path, "manage.py"))
            ):
                return item_path
    except:
        pass

    # 未找到 manage.py
    return None


def find_venv(start_dir):
    """尋找虛擬環境目錄"""
    # 檢查常見的虛擬環境名稱
    venv_names = [
        "venv",
        "env",
        ".venv",
        "virtualenv",
        "testvenv",
        "djangovenv",
        "django_venv",
        "myenv",
        "py_env",
    ]

    # 檢查自訂虛擬環境名稱（包含關鍵詞）
    def is_custom_venv(name):
        """判斷是否是自訂虛擬環境目錄"""
        keywords = ["venv", "env", "virtual", "python"]
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in keywords)

    # 檢查當前目錄和父目錄
    current_dir = start_dir
    for _ in range(3):  # 最多向上檢查3層
        # 先檢查常見虛擬環境名稱
        for venv_name in venv_names:
            venv_path = os.path.join(current_dir, venv_name)
            if os.path.exists(venv_path) and os.path.exists(
                os.path.join(venv_path, "Scripts", "activate.bat")
            ):
                return venv_path

        # 檢查目錄中所有可能的虛擬環境文件夾
        try:
            for item in os.listdir(current_dir):
                if not os.path.isdir(os.path.join(current_dir, item)):
                    continue

                # 如果文件夾名稱符合虛擬環境特徵
                if is_custom_venv(item):
                    venv_path = os.path.join(current_dir, item)
                    # 確認是否有 activate.bat
                    if os.path.exists(
                        os.path.join(venv_path, "Scripts", "activate.bat")
                    ):
                        return venv_path
        except (PermissionError, OSError):
            pass

        # 向上一層目錄
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 已經在根目錄
            break
        current_dir = parent_dir

    return None


def find_env_file(project_dir):
    """尋找 .env 文件"""
    env_file_patterns = [
        os.path.join(project_dir, ".env.local"),
        os.path.join(project_dir, ".env"),
        os.path.join(os.path.dirname(project_dir), ".env.local"),
        os.path.join(os.path.dirname(project_dir), ".env"),
    ]

    for pattern in env_file_patterns:
        if os.path.exists(pattern):
            return pattern

    return None


def load_env_file(env_file_path):
    """從.env文件加載環境變數"""
    if not env_file_path or not os.path.exists(env_file_path):
        return False, "找不到環境變數文件"

    try:
        # 讀取環境變數
        env_vars = {}
        with open(env_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    name, value = line.split("=", 1)
                    env_vars[name.strip()] = value.strip()
                    # 同時設置當前進程的環境變數
                    os.environ[name.strip()] = value.strip()

        global ENV_VARS
        ENV_VARS = env_vars
        return True, f"已加載環境變數: {env_file_path}"
    except Exception as e:
        return False, f"加載環境變數時出錯: {str(e)}"


def create_bat_and_run(
    commands,
    title=None,
    wait=False,
    directory=None,
    venv_activate=None,
    env_vars=None,
    admin=True,  # 預設使用管理員權限
):
    """
    建立臨時 .bat 文件，並在新 CMD 視窗中執行命令

    參數:
    - commands: 要執行的命令列表
    - title: CMD 視窗標題
    - wait: 是否在指令執行後等待用戶按鍵
    - directory: 執行命令的目錄
    - venv_activate: 虛擬環境 activate.bat 的路徑
    - env_vars: 環境變數字典
    - admin: 是否以管理員權限執行
    """
    # 創建臨時 .bat 文件
    with tempfile.NamedTemporaryFile(
        suffix=".bat", delete=False, mode="w", encoding="utf-8"
    ) as bat_file:
        bat_path = bat_file.name

        # 寫入批處理文件內容
        bat_file.write("@echo off\n")
        bat_file.write("chcp 65001 >nul\n")  # 設置UTF-8編碼

        if title:
            bat_file.write(f"title {title}\n")

        # 切換到項目目錄
        if directory and os.path.exists(directory):
            bat_file.write(f'cd /d "{directory}"\n')

        # 啟用虛擬環境 (如果有)
        if venv_activate and os.path.exists(venv_activate):
            bat_file.write(f"echo 正在啟用虛擬環境...\n")
            bat_file.write(f'call "{venv_activate}"\n')

        # 設置環境變數
        if env_vars and isinstance(env_vars, dict):
            bat_file.write(f"echo 正在設置環境變數...\n")
            for name, value in env_vars.items():
                bat_file.write(f'set "{name}={value}"\n')

        # 寫入要執行的命令
        bat_file.write("\n")
        for cmd in commands:
            bat_file.write(f"{cmd}\n")

        # 如果需要，添加等待命令
        if wait:
            bat_file.write("\necho.\n")
            bat_file.write("echo 命令執行完成。按任意鍵關閉視窗...\n")
            bat_file.write("pause > nul\n")

    # 在新 CMD 視窗執行 .bat 文件
    try:
        if admin:
            # 使用 PowerShell 以管理員權限啟動
            admin_cmd = f'powershell -Command "Start-Process cmd -ArgumentList \'/c ""{bat_path}""\'  -Verb RunAs"'
            subprocess.Popen(admin_cmd, shell=True)
        else:
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "cmd", "/k", bat_path], shell=True
            )

        success = True
        message = f"已在新視窗啟動: {title or commands[0]}"
    except Exception as e:
        success = False
        message = f"啟動新視窗時發生錯誤: {e}"

    # 一段時間後自動刪除臨時文件 (避免累積太多)
    def delete_temp_file():
        time.sleep(5)
        try:
            if os.path.exists(bat_path):
                os.remove(bat_path)
        except:
            pass

    threading.Thread(target=delete_temp_file, daemon=True).start()

    return success, message


def select_project_directory():
    """
    彈出文件對話框，讓使用者選擇 Django 項目目錄

    返回:
    - 選擇的目錄路徑，或者 None 如果用戶取消選擇
    """
    # 檢查 tkinter 是否可用
    if not TKINTER_AVAILABLE:
        print("⚠️ GUI 檔案選擇不可用 - 缺少 tkinter 支援")
        print("⚠️ 將使用自動偵測或手動輸入路徑")

        # 嘗試從當前目錄開始
        current_dir = os.getcwd()
        manage_dir = find_manage_py(current_dir)
        if manage_dir:
            return manage_dir

        # 如果自動偵測失敗，讓用戶直接輸入路徑
        print("\n請輸入 Django 項目目錄路徑 (包含 manage.py 的目錄):")
        user_dir = input("> ").strip()

        if not user_dir:
            return None

        # 檢查輸入的目錄是否存在
        if not os.path.exists(user_dir):
            print(f"⚠️ 路徑不存在: {user_dir}")
            return None

        # 檢查是否含有 manage.py
        if os.path.exists(os.path.join(user_dir, "manage.py")):
            return user_dir
        else:
            # 嘗試在子目錄中查找
            manage_dir = find_manage_py(user_dir)
            if manage_dir:
                return manage_dir
            else:
                print(f"⚠️ 找不到 manage.py 在: {user_dir}")
                return None

    # 使用 tkinter GUI 選擇
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口

    messagebox.showinfo(
        "選擇 Django 項目", "請選擇您的 Django 多租戶項目目錄 (包含 manage.py 的目錄)"
    )

    directory = filedialog.askdirectory(title="選擇 Django 項目目錄")

    if not directory:
        messagebox.showwarning("警告", "未選擇目錄，將嘗試自動偵測")
        return None

    # 檢查選擇的目錄是否包含 manage.py
    if not os.path.exists(os.path.join(directory, "manage.py")):
        # 嘗試在子目錄中查找
        manage_dir = find_manage_py(directory)
        if manage_dir:
            directory = manage_dir
        else:
            messagebox.showerror(
                "錯誤", "所選目錄不包含 Django 項目 (找不到 manage.py)"
            )
            return None

    return directory


def display_detection_results(project_dir, venv_dir, env_file):
    """
    顯示自動偵測結果
    """
    message = (
        f"項目目錄: {project_dir}\n"
        f"虛擬環境: {venv_dir or '未找到'}\n"
        f"環境文件: {env_file or '未找到'}\n"
    )

    # 檢查 tkinter 是否可用
    if TKINTER_AVAILABLE:
        root = tk.Tk()
        root.withdraw()  # 隱藏主窗口
        messagebox.showinfo("自動偵測結果", message)
    else:
        print("\n========== 自動偵測結果 ==========")
        print(message)
        print("==================================")


# Django 命令相關函數
def run_django_server(project_dir, venv_activate, env_vars=None):
    """啟動 Django 開發伺服器"""
    return create_bat_and_run(
        ["python manage.py runserver"],
        title="Django Runserver",
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def run_django_shell(project_dir, venv_activate, env_vars=None):
    """啟動 Django Shell"""
    return create_bat_and_run(
        ["python manage.py shell"],
        title="Django Shell",
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def migrate_schemas_shared(project_dir, venv_activate, env_vars=None):
    """執行共享租戶的資料庫遷移"""
    return create_bat_and_run(
        ["python manage.py migrate_schemas --shared"],
        title="Django Migrate Schemas (Shared)",
        wait=True,
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def migrate_schemas_all(project_dir, venv_activate, env_vars=None):
    """執行所有租戶的資料庫遷移"""
    return create_bat_and_run(
        ["python manage.py migrate_schemas"],
        title="Django Migrate All Schemas",
        wait=True,
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def create_tenant_superuser(schema, project_dir, venv_activate, env_vars=None):
    """為指定租戶創建超級使用者"""
    if not schema or not schema.strip():
        return False, "請提供有效的 schema 名稱"

    return create_bat_and_run(
        [f"python manage.py tenant_command createsuperuser --schema={schema}"],
        title=f"Create Superuser for {schema}",
        wait=True,
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def collectstatic(project_dir, venv_activate, env_vars=None):
    """收集靜態文件"""
    return create_bat_and_run(
        ["python manage.py collectstatic --noinput"],
        title="Django Collectstatic",
        wait=True,
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


def open_venv_shell(project_dir, venv_activate, env_vars=None):
    """打開一個已啟用虛擬環境的命令提示符"""
    if not venv_activate:
        return False, "找不到虛擬環境，無法啟動 venv Shell"

    return create_bat_and_run(
        [
            "echo 已進入 Django 專案虛擬環境",
            "echo 當前目錄: %CD%",
            "echo Python 版本: ",
            "python --version",
            "echo.",
            "echo 可直接輸入 Django 命令，例如: python manage.py runserver",
            "cmd /k",  # 保持命令窗口開啟
        ],
        title="Django venv Shell",
        directory=project_dir,
        venv_activate=venv_activate,
        env_vars=env_vars,
        admin=True,  # 使用管理員權限
    )


# DNS 管理相關函數
def create_dns_management_tool():
    """創建並啟動本地 DNS 管理工具"""
    # 使用臨時文件而不是固定文件，避免重複執行的問題
    try:
        with tempfile.NamedTemporaryFile(
            suffix=".bat", delete=False, mode="w", encoding="utf-8"
        ) as dns_script_file:
            dns_script_path = dns_script_file.name

            # DNS 腳本內容
            dns_script = """@echo off
setlocal enabledelayedexpansion

:menu
cls
echo ============================
echo Local DNS Management Tool
echo ============================
echo.
echo 1. Add new domain to hosts file
echo 2. View current hosts entries
echo 3. Edit hosts file manually
echo 4. Exit
echo.
set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" goto add_domain
if "%choice%"=="2" goto view_hosts
if "%choice%"=="3" goto edit_hosts
if "%choice%"=="4" goto end

echo Invalid choice, please try again.
timeout /t 2 >nul
goto menu

:add_domain
cls
echo ============================
echo Add New Domain
echo ============================
echo.

set /p domain=Enter domain to register (e.g., tenant1.localhost): 

if "%domain%"=="" (
    echo Error: No domain entered!
    timeout /t 2 >nul
    goto menu
)

echo.
echo Adding local host record 127.0.0.1 %domain% ...

powershell -Command "Start-Process cmd -ArgumentList '/c echo 127.0.0.1 %domain% >> %%WINDIR%%\\System32\\drivers\\etc\\hosts && echo Successfully added host record for %domain%! && pause' -Verb RunAs"

goto menu

:view_hosts
cls
echo ============================
echo Current Hosts File Entries
echo ============================
echo.
echo Showing non-comment lines from hosts file:
echo.
findstr /v "^#" %WINDIR%\\System32\\drivers\\etc\\hosts | findstr /v "^$"
echo.
echo ----------------------------
echo.
pause
goto menu

:edit_hosts
cls
echo ============================
echo Edit Hosts File (Admin)
echo ============================
echo.
echo This will open the hosts file in Notepad with admin privileges.
echo You can manually edit or delete entries as needed.
echo.
echo Press any key to continue...
pause >nul

powershell -Command "Start-Process notepad -ArgumentList '%WINDIR%\\System32\\drivers\\etc\\hosts' -Verb RunAs"

goto menu

:end
exit
"""
            dns_script_file.write(dns_script)

        # 使用管理員權限啟動
        admin_cmd = f'powershell -Command "Start-Process cmd -ArgumentList \'/c ""{dns_script_path}""\'  -Verb RunAs"'
        subprocess.Popen(admin_cmd, shell=True)

        # 一段時間後自動刪除臨時文件
        def delete_temp_dns_file():
            time.sleep(10)  # 給足夠時間啟動
            try:
                if os.path.exists(dns_script_path):
                    os.remove(dns_script_path)
            except:
                pass

        threading.Thread(target=delete_temp_dns_file, daemon=True).start()

        success = True
        message = "已啟動本地 DNS 管理工具 (英文介面)"
    except Exception as e:
        success = False
        message = f"啟動 DNS 管理工具時發生錯誤: {e}"

    return success, message


def inspect_tenants(project_dir, venv_activate):
    """檢查所有租戶的狀態（確保視窗不會自動關閉）"""
    try:
        # 創建一個批處理文件
        with tempfile.NamedTemporaryFile(
            suffix=".bat", delete=False, mode="w", encoding="utf-8"
        ) as batch_file:
            batch_path = batch_file.name

            # 批處理文件內容
            batch_file.write(
                f"""@echo off
chcp 65001 >nul
cd /d "{project_dir}"

REM 啟用虛擬環境（如果存在）
if exist "{venv_activate}" (
    call "{venv_activate}"
)

echo === 執行租戶檢查 ===
echo.
echo === 公共租戶名稱 ===
python manage.py shell -c "from django_tenants.utils import get_public_schema_name; print('公共租戶:', get_public_schema_name())"
echo.
echo === 租戶列表 ===
python manage.py shell -c "from django_tenants.utils import get_tenant_model; [print(t.schema_name) for t in get_tenant_model().objects.all()]"
echo.
echo === 租戶域名 ===
python manage.py shell -c "from django_tenants.utils import get_tenant_model, get_tenant_domain_model; tenants = get_tenant_model().objects.all(); domains = get_tenant_domain_model().objects.all(); [print(f'{{t.schema_name}} 域名: {{\\\"、\\\".join([d.domain for d in domains.filter(tenant=t)])}}') for t in tenants]"
echo.
echo === 超級使用者 ===
python manage.py shell -c "from django_tenants.utils import get_tenant_model; tenants = list(get_tenant_model().objects.all()); print(f'發現 {{len(tenants)}} 個租戶，將逐一檢查超級使用者...')"
echo.
echo --- 檢查公共租戶的超級使用者 ---
python manage.py shell -c "from django.contrib.auth import get_user_model; print(f'超級使用者: {{\\\"、\\\".join([u.username for u in get_user_model().objects.filter(is_superuser=True)])}}')"
echo.
echo --- 檢查其他租戶的超級使用者 (可能需要時間) ---
python manage.py shell -c "from django_tenants.utils import get_tenant_model; tenants = [t for t in get_tenant_model().objects.all() if t.schema_name != 'public']; [print(f'檢查租戶 {{t.schema_name}}...') for t in tenants]"
echo.
echo 對每個非公共租戶執行檢查...
python manage.py tenant_command shell -c "from django.contrib.auth import get_user_model; print(f'當前租戶超級使用者: {{\\\"、\\\".join([u.username for u in get_user_model().objects.filter(is_superuser=True)])}}')" --schema=tenant1
echo.
echo === 檢查完成 ===
echo.
echo 請按任意鍵關閉此視窗...
pause > nul
"""
            )

        # 以管理員權限運行，並使用 cmd /K 保持視窗開啟
        # 注意這裡使用 cmd /K 代替 cmd /C
        admin_cmd = f'powershell -Command "Start-Process cmd -ArgumentList \'/K "{batch_path}"\'  -Verb RunAs"'
        subprocess.Popen(admin_cmd, shell=True)

        # 一段時間後刪除臨時文件
        def delete_temp_file():
            time.sleep(10)  # 給足夠時間執行
            try:
                if os.path.exists(batch_path):
                    os.remove(batch_path)
            except:
                pass

        threading.Thread(target=delete_temp_file, daemon=True).start()

        return True, "已啟動租戶檢查，請查看新開啟的視窗"

    except Exception as e:
        return False, f"啟動租戶檢查時發生錯誤: {str(e)}"


def setup_environment():
    """設置環境並偵測項目路徑"""
    global PROJECT_DIR, VENV_DIR, VENV_PYTHON, VENV_ACTIVATE, ENV_FILE, ENV_VARS

    # 判斷是否是打包後的 EXE
    if getattr(sys, "frozen", False):
        # 如果是打包後的 EXE
        exe_dir = os.path.dirname(sys.executable)
        start_dir = os.path.abspath(os.path.join(exe_dir, ".."))
    else:
        # 如果是直接執行 Python 腳本
        start_dir = os.path.dirname(os.path.abspath(__file__))

    # 先嘗試從用戶選擇獲取項目目錄
    selected_dir = select_project_directory()

    if selected_dir:
        PROJECT_DIR = selected_dir
    else:
        # 如果用戶取消選擇，則自動偵測
        PROJECT_DIR = find_manage_py(start_dir)
        if not PROJECT_DIR:
            PROJECT_DIR = find_manage_py(os.path.dirname(start_dir))
            if not PROJECT_DIR:
                print("⚠️ 無法找到 manage.py，將使用當前目錄作為項目目錄")
                PROJECT_DIR = start_dir

    # 找到虛擬環境
    VENV_DIR = find_venv(start_dir)
    if not VENV_DIR:
        VENV_DIR = find_venv(PROJECT_DIR)

    # 如果找到了虛擬環境，設置相關路徑
    if VENV_DIR:
        VENV_PYTHON = os.path.join(VENV_DIR, "Scripts", "python.exe")
        VENV_ACTIVATE = os.path.join(VENV_DIR, "Scripts", "activate.bat")
    else:
        print("⚠️ 無法找到虛擬環境，將使用系統 Python")
        VENV_PYTHON = "python"
        VENV_ACTIVATE = None

    # 找到 .env 文件
    ENV_FILE = find_env_file(PROJECT_DIR)

    # 讀取環境變數
    ENV_VARS = {}
    if ENV_FILE:
        load_env_file(ENV_FILE)

    # 顯示偵測結果
    display_detection_results(PROJECT_DIR, VENV_DIR, ENV_FILE)


def show_menu():
    """顯示主選單"""
    print(
        """
===============================
🛠 Django 多租戶開發工具箱 v1.0
===============================
[1] 啟動 runserver
[2] 進入 Django shell
[3] migrate_schemas --shared
[4] migrate_schemas 所有租戶
[5] 建立 superuser（輸入 schema）
[6] collectstatic
[7] 檢查所有租戶（superuser + migration）
[8] 本地 DNS 管理工具（需要管理員權限）
[0] 進入虛擬環境終端機
[x] 離開
===============================
"""
    )


def main():
    """主程序入口點"""
    # 設置環境
    setup_environment()

    # 檢查是否找到 manage.py
    if not os.path.exists(os.path.join(PROJECT_DIR, "manage.py")):
        print("❌ 警告: 在項目目錄中找不到 manage.py!")

    while True:
        show_menu()
        choice = input("請輸入選項編號：").strip().lower()

        if choice == "1":
            success, message = run_django_server(PROJECT_DIR, VENV_ACTIVATE, ENV_VARS)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "2":
            success, message = run_django_shell(PROJECT_DIR, VENV_ACTIVATE, ENV_VARS)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "3":
            success, message = migrate_schemas_shared(
                PROJECT_DIR, VENV_ACTIVATE, ENV_VARS
            )
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "4":
            success, message = migrate_schemas_all(PROJECT_DIR, VENV_ACTIVATE, ENV_VARS)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "5":
            schema = input("請輸入租戶 schema 名稱：").strip()
            success, message = create_tenant_superuser(
                schema, PROJECT_DIR, VENV_ACTIVATE, ENV_VARS
            )
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "6":
            success, message = collectstatic(PROJECT_DIR, VENV_ACTIVATE, ENV_VARS)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "7":
            success, message = inspect_tenants(PROJECT_DIR, VENV_ACTIVATE)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "8":
            success, message = create_dns_management_tool()
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "0":
            success, message = open_venv_shell(PROJECT_DIR, VENV_ACTIVATE, ENV_VARS)
            print(f"{'✅' if success else '❌'} {message}")
        elif choice == "x":
            print("👋 再見！")
            break
        else:
            print("❌ 無效選項，請重新輸入")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        input("\n👋 程式結束，請按 Enter 離開...")
