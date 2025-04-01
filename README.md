# Django多租戶工具箱 (Django Tenants ToolBox)

A Windows-based GUI helper for Django Tenants. No coding required. Easily run migrate_schemas, create superusers, inspect tenant status, and more.

一款專為Django多租戶應用開發者設計的便捷工具箱。該工具旨在簡化多租戶應用的日常開發和管理工作，無需編程經驗即可使用。

![Django多租戶工具箱](https://img.shields.io/badge/Django-多租戶工具箱-brightgreen)
![版本](https://img.shields.io/badge/版本-1.0-blue)
![開源許可](https://img.shields.io/badge/許可-MIT_(No_Resell)-yellow)

## 功能特點

- 🚀 簡化 Django 多租戶應用的常見操作
- 🔄 自動偵測 Django 項目和虛擬環境
- 🔧 一鍵執行資料庫遷移、建立超級用戶等操作
- 🌐 內建本地 DNS 管理工具，便於測試
- 📊 檢查租戶狀態和配置信息
- 💻 使用圖形介面選擇項目目錄
- 🛡️ 自動以管理員權限執行命令，減少錯誤

## 安裝指南

### 方法 1: 使用預編譯的 EXE 文件（推薦）

1. 從 [Releases](https://github.com/你的用戶名/django-tenants-toolbox/releases) 頁面下載最新版本
2. 解壓縮下載的 ZIP 文件
3. 執行 `install.bat` 安裝程序，會自動在桌面創建捷徑

### 方法 2: 從源碼運行

1. 確保已安裝 Python 3.7+
2. 克隆此代碼庫：`git clone https://github.com/你的用戶名/django-tenants-toolbox.git`
3. 進入項目目錄：`cd django-tenants-toolbox`
4. 直接運行：`python main.py`

## 使用方法

1. 啟動工具箱（通過桌面捷徑或直接運行 EXE 文件）
2. 選擇 Django 項目目錄（包含 manage.py 的目錄）
3. 使用選單選擇要執行的操作：

| 選項 | 功能 |
|------|------|
| 1 | 啟動 Django 開發服務器 (runserver) |
| 2 | 進入 Django shell |
| 3 | 執行共享租戶的資料庫遷移 (migrate_schemas --shared) |
| 4 | 執行所有租戶的資料庫遷移 (migrate_schemas) |
| 5 | 為特定租戶創建超級用戶 |
| 6 | 收集靜態文件 (collectstatic) |
| 7 | 檢查所有租戶狀態 |
| 8 | 啟動本地 DNS 管理工具 |
| 0 | 進入虛擬環境終端機 |

## 使用建議

- 將工具箱放在您的 Django 專案目錄中（與 manage.py 同級）
- 使用選項 1-4 進行資料庫遷移，選項 7 檢查租戶狀態
- 使用選項 8 管理本地 DNS 記錄以便於測試不同租戶域名

## 常見問題

**Q: 工具找不到我的 Django 項目?**
A: 請確保選擇的目錄中包含 manage.py 文件，或者將工具箱直接放在項目目錄中運行。

**Q: 執行命令出現權限問題?**
A: 本工具會自動嘗試以管理員權限執行命令。如果仍有問題，請右鍵以管理員身份運行。

**Q: 我沒有編程經驗，能使用這個工具嗎?**
A: 可以！本工具設計為無需編程經驗即可使用，提供了簡單的菜單界面。

## 系統要求

- Windows 7/8/10/11
- Python 3.7+ (如果從源碼運行)
- 不需要管理員權限（程序會在需要時自動請求）

## 貢獻指南

歡迎提交 Pull Requests 和 Issues 來幫助改進這個工具！

1. Fork 這個項目
2. 創建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 許可證

本項目採用修改版 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件。
禁止用於商業轉售用途。

## 聯繫方式

如有問題或建議，請通過 GitHub Issues 提交。

---

感謝使用 Django多租戶工具箱！
