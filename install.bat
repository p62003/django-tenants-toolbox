@echo off
cd /d %~dp0
chcp 65001 >nul

echo ===== Django多租戶工具箱安裝程序 =====
echo.

REM 檢查是否已有EXE檔案
if not exist DjangoTenantsToolBox.exe (
    echo [錯誤] 找不到 DjangoTenantsToolBox.exe 檔案
    echo 請確保您已完整下載並解壓縮所有檔案。
    pause
    exit /b 1
)

echo [提示] 找到 DjangoTenantsToolBox.exe 檔案
echo [提示] 正在創建桌面捷徑...

REM 使用PowerShell創建桌面捷徑
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\Django多租戶工具箱.lnk'); $Shortcut.TargetPath = '%~dp0\DjangoTenantsToolBox.exe'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = 'Django多租戶工具箱'; if (Test-Path '%~dp0\icon.ico') { $Shortcut.IconLocation = '%~dp0\icon.ico' }; $Shortcut.Save()"

REM 創建啟動批處理檔案（備用）
echo @echo off > 啟動工具箱.bat
echo start DjangoTenantsToolBox.exe >> 啟動工具箱.bat

echo.
echo [完成] Django多租戶工具箱安裝完成！
echo.
echo 您現在可以：
echo 1. 直接雙擊桌面上的「Django多租戶工具箱」捷徑啟動
echo 2. 雙擊「啟動工具箱.bat」批處理檔啟動
echo 3. 直接執行 DjangoTenantsToolBox.exe 啟動
echo.
echo 使用建議：
echo - 將工具箱放在您的 Django 專案目錄中（與 manage.py 同級）使用
echo - 使用選項 1-4 進行資料庫遷移，選項 7 檢查租戶狀態
echo - 如需使用 DNS 功能，請使用選項 8-9（需要管理員權限）
echo.
echo 感謝使用Django多租戶工具箱！
pause