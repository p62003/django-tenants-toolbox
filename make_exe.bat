@echo off
cd /d %~dp0
chcp 65001 >nul

echo [測試] 檢查目錄結構...
if not exist main.py (
  echo [ERROR] 找不到主入口 main.py，請確保此文件存在於根目錄
  pause
  exit /b 1
)

echo [測試] 尋找虛擬環境...
set VENV_FOUND=0
set VENV_PATH=

REM 搜尋常見虛擬環境名稱
for %%v in (venv env .venv virtualenv testvenv djangovenv django_venv myenv) do (
  if exist %%v\Scripts\activate.bat (
    set VENV_PATH=%%v
    set VENV_FOUND=1
    echo [成功] 找到虛擬環境: %%v
    goto found_venv
  )
)

REM 搜尋目錄中可能的虛擬環境
for /d %%d in (*) do (
  if exist %%d\Scripts\activate.bat (
    set VENV_PATH=%%d
    set VENV_FOUND=1
    echo [成功] 找到可能的虛擬環境: %%d
    goto found_venv
  )
)

:not_found_venv
echo [警告] 找不到現有虛擬環境，將嘗試創建...
python -m venv venv
if errorlevel 1 (
  echo [錯誤] 無法創建虛擬環境，將嘗試使用系統 Python
  set VENV_FOUND=0
  set VENV_PATH=
) else (
  set VENV_PATH=venv
  set VENV_FOUND=1
  echo [成功] 已創建新的虛擬環境: venv
)
goto continue_process

:found_venv
echo [測試] 將使用虛擬環境: %VENV_PATH%

:continue_process
REM 使用找到的虛擬環境或系統 Python
if %VENV_FOUND%==1 (
  echo [測試] 啟用虛擬環境...
  call %VENV_PATH%\Scripts\activate.bat
) else (
  echo [警告] 將使用系統 Python
)

echo [測試] 顯示當前 Python 路徑：
where python

echo [測試] 顯示 Python 版本：
python --version

echo [測試] 安裝/更新必要套件...
pip install -U pyinstaller python-dotenv

echo [!] 開始使用 pyinstaller 打包 DjangoTenantsToolBox.exe ...

REM 檢查是否存在圖示文件
set USE_ICON=
if exist icon.ico (
  set USE_ICON=--icon=icon.ico
  echo [INFO] 找到圖示檔案，將使用 icon.ico 作為程式圖示
) else (
  echo [INFO] 圖示檔案不存在，將使用默認圖示
)

REM 使用自動生成的 .spec 文件打包
pyinstaller --noconfirm --clean ^
  --name=DjangoTenantsToolBox ^
  --hidden-import=tkinter ^
  --hidden-import=tkinter.filedialog ^
  --hidden-import=tkinter.messagebox ^
  %USE_ICON% ^
  --onefile ^
  main.py

if errorlevel 1 (
  echo [錯誤] pyinstaller 執行失敗。嘗試使用另一種方法...
  
  REM 嘗試使用最基本的選項重新打包
  echo [!] 使用基本選項重試打包...
  pyinstaller --noconfirm --clean --onefile main.py
  
  if errorlevel 1 (
    echo [ERROR] 打包失敗，請檢查錯誤訊息。
    pause
    exit /b 1
  )
  
  REM 重命名生成的EXE文件
  if exist dist\main.exe (
    move dist\main.exe dist\DjangoTenantsToolBox.exe
  )
)

echo [!] 打包成功！

REM 創建或清空輸出目錄
if not exist dist mkdir dist
if not exist dist\release mkdir dist\release
if exist dist\release\*.* del /Q dist\release\*.*

REM 複製EXE文件到輸出目錄
if exist dist\DjangoTenantsToolBox.exe (
  copy dist\DjangoTenantsToolBox.exe dist\release\
) else (
  echo [警告] 找不到生成的EXE文件
  pause
  exit /b 1
)

REM 複製其他必要文件
copy install.bat dist\release\
if exist icon.ico copy icon.ico dist\release\
if exist README.md copy README.md dist\release\

REM 創建啟動批處理文件
echo @echo off > dist\release\啟動工具箱.bat
echo start DjangoTenantsToolBox.exe >> dist\release\啟動工具箱.bat

echo.
echo [完成] 打包和準備發布文件完成！
echo.
echo 可發布文件位於 dist\release 目錄中:
echo       - DjangoTenantsToolBox.exe (主程式)
echo       - install.bat (安裝腳本)
echo       - 啟動工具箱.bat (快速啟動批處理)
echo       - README.md (使用說明)
echo       - icon.ico (如果存在)
echo.
echo 您可以將 dist\release 目錄中的所有文件上傳到 GitHub 發布。
echo 使用者下載後只需執行 install.bat 即可開始使用。
pause