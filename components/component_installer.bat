@echo off
chcp 65001 >nul

REM =============================================
REM 静默退出优化组件 - 一键安装脚本
REM 版本: v1.0
REM 作者: @橘生淮北
REM 功能: 将静默退出优化组件复制到指定项目中
REM =============================================

echo =============================================
echo        📦 静默退出优化组件安装器
echo =============================================
echo.

REM 获取当前组件目录
set COMPONENT_DIR=%~dp0
set TARGET_DIR=%1

REM 如果没有提供目标目录，提示用户输入
if "%TARGET_DIR%"=="" (
    echo [INFO] 请指定目标项目目录:
    echo.
    echo 使用方法:
    echo   component_installer.bat "D:\MyProject"
    echo.
    echo 或者拖拽目标项目文件夹到此脚本上
    echo.
    pause
    exit /b 1
)

REM 检查目标目录是否存在
if not exist "%TARGET_DIR%" (
    echo [ERROR] 目标目录不存在: %TARGET_DIR%
    pause
    exit /b 1
)

echo [INFO] 组件源目录: %COMPONENT_DIR%
echo [INFO] 目标项目目录: %TARGET_DIR%
echo.

REM 创建组件目录
set TARGET_COMPONENT_DIR=%TARGET_DIR%\components
if not exist "%TARGET_COMPONENT_DIR%" (
    mkdir "%TARGET_COMPONENT_DIR%"
    echo [INFO] 创建组件目录: components\
)

REM 复制组件文件
echo [STEP 1/3] 复制静默退出基类...
copy "%COMPONENT_DIR%silent_exit_gui_base.py" "%TARGET_COMPONENT_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] 复制 silent_exit_gui_base.py 失败
    pause
    exit /b 1
)

echo [STEP 2/3] 复制打包脚本...
copy "%COMPONENT_DIR%silent_exit_packager.bat" "%TARGET_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] 复制 silent_exit_packager.bat 失败
    pause
    exit /b 1
)

echo [STEP 3/3] 复制使用文档...
copy "%COMPONENT_DIR%README.md" "%TARGET_COMPONENT_DIR%\" >nul
if errorlevel 1 (
    echo [ERROR] 复制 README.md 失败
    pause
    exit /b 1
)

REM 创建示例代码
echo [INFO] 创建示例代码...
(
echo # 静默退出优化示例
echo # 使用方法:
echo #   1. 从 components.silent_exit_gui_base 导入 SilentExitGUIBase
echo #   2. 继承该类并实现 setup_ui 方法
echo #   3. 使用 silent_exit_packager.bat 进行打包
echo.
echo import tkinter as tk
echo from components.silent_exit_gui_base import SilentExitGUIBase
echo.
echo class MyApp(SilentExitGUIBase^):
echo     def setup_ui(self^):
echo         # 设置窗口
echo         self.root.geometry("400x300"^)
echo         
echo         # 添加你的UI组件
echo         label = tk.Label(self.root, text="Hello, World!"^)
echo         label.pack(pady=20^)
echo.
echo if __name__ == "__main__":
echo     root = tk.Tk(^)
echo     app = MyApp(root, "我的应用程序", "app_icon.ico"^)
echo     app.setup_ui(^)
echo     root.mainloop(^)
) > "%TARGET_DIR%\silent_exit_example.py"

echo.
echo =============================================
echo        ✅ 组件安装成功完成！
echo =============================================
echo.
echo 📁 已安装的文件:
echo   • %TARGET_DIR%\components\silent_exit_gui_base.py
echo   • %TARGET_DIR%\components\README.md  
echo   • %TARGET_DIR%\silent_exit_packager.bat
echo   • %TARGET_DIR%\silent_exit_example.py
echo.
echo 🚀 快速开始:
echo   1. 查看 silent_exit_example.py 了解使用方法
echo   2. 修改 silent_exit_packager.bat 中的项目配置
echo   3. 运行 silent_exit_packager.bat 进行打包
echo.
echo 📖 详细文档:
echo   查看 components\README.md 获取完整使用指南
echo.
echo =============================================
pause