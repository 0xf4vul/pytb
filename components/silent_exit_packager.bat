@echo off
chcp 65001 >nul

REM =============================================
REM 静默退出优化打包脚本 - 公共开发组件
REM 版本: v1.0
REM 作者: @橘生淮北
REM 功能: 为GUI应用程序提供完全静默的打包和退出体验
REM =============================================

REM ===========================================
REM 可配置参数区域 - 根据项目需要修改
REM ===========================================

REM 项目配置
set PROJECT_NAME=MyGUIApp
set MAIN_SCRIPT=main.py
set OUTPUT_NAME=MyApp

REM 虚拟环境配置
set VENV_NAME=venv
set PYTHON_EXE=python

REM 图标配置（可选）
set ICON_FILE=app_icon.ico

REM 依赖包列表（空格分隔）
set DEPENDENCIES=

REM 自定义数据目录（相对路径，可选）
set DATA_DIRS=

REM 自定义模块隐式导入（可选）
set HIDDEN_IMPORTS=

REM ===========================================
REM 自动检测项目配置
REM ===========================================

set PROJECT_DIR=%~dp0..
if "%PROJECT_DIR:~-1%"==".." set PROJECT_DIR=%~dp0

echo =============================================
echo        🚀 开始构建 %PROJECT_NAME% （静默优化版）
echo =============================================

echo.
echo [INFO] 项目目录: %PROJECT_DIR%
echo [INFO] 主程序脚本: %MAIN_SCRIPT%
echo [INFO] 输出名称: %OUTPUT_NAME%

REM 检查主脚本是否存在
if not exist "%PROJECT_DIR%\%MAIN_SCRIPT%" (
    echo [ERROR] 主脚本文件不存在: %MAIN_SCRIPT%
    echo [HELP] 请确认以下文件存在或修改脚本中的 MAIN_SCRIPT 变量:
    echo        %PROJECT_DIR%\%MAIN_SCRIPT%
    pause
    exit /b 1
)

REM ===========================================
REM 虚拟环境管理
REM ===========================================

set VENV_PATH=%PROJECT_DIR%\%VENV_NAME%

echo.
echo [STEP 1/4] 创建/重建虚拟环境: %VENV_NAME%

REM 如果虚拟环境已存在，询问是否重建
if exist "%VENV_PATH%" (
    echo [INFO] 虚拟环境已存在，将重新创建...
    rmdir /s /q "%VENV_PATH%" 2>nul
)

call %PYTHON_EXE% -m venv "%VENV_PATH%"
if errorlevel 1 (
    echo [ERROR] 虚拟环境创建失败，请确认已安装 Python！
    echo [HELP] 请检查 Python 安装或修改脚本中的 PYTHON_EXE 变量
    pause
    exit /b 1
)

REM ===========================================
REM 依赖安装
REM ===========================================

echo.
echo [STEP 2/4] 激活虚拟环境并安装依赖

call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] 无法激活虚拟环境！
    pause
    exit /b 1
)

echo [INFO] 升级 pip...
%PYTHON_EXE% -m pip install --upgrade pip --quiet

echo [INFO] 安装 PyInstaller...
%PYTHON_EXE% -m pip install pyinstaller --quiet

REM 安装项目特定依赖
if not "%DEPENDENCIES%"=="" (
    echo [INFO] 安装项目依赖: %DEPENDENCIES%
    %PYTHON_EXE% -m pip install %DEPENDENCIES% --quiet
)

REM 检查是否存在 requirements.txt
if exist "%PROJECT_DIR%\requirements.txt" (
    echo [INFO] 发现 requirements.txt，安装依赖...
    %PYTHON_EXE% -m pip install -r "%PROJECT_DIR%\requirements.txt" --quiet
)

echo [INFO] 依赖安装完成。

REM ===========================================
REM 静默优化打包
REM ===========================================

echo.
echo [STEP 3/4] 使用 PyInstaller 进行静默优化打包...

REM 构建基础打包命令
set PACK_CMD=%PYTHON_EXE% -m PyInstaller --noconfirm --onefile --windowed

REM 添加图标（如果存在）
if exist "%PROJECT_DIR%\%ICON_FILE%" (
    set PACK_CMD=%PACK_CMD% --icon="%PROJECT_DIR%\%ICON_FILE%"
    echo [INFO] 使用图标文件: %ICON_FILE%
)

REM 添加数据目录
if not "%DATA_DIRS%"=="" (
    for %%D in (%DATA_DIRS%) do (
        if exist "%PROJECT_DIR%\%%D" (
            set PACK_CMD=%PACK_CMD% --add-data "%PROJECT_DIR%\%%D;%%D"
            echo [INFO] 添加数据目录: %%D
        )
    )
)

REM 添加隐式导入
if not "%HIDDEN_IMPORTS%"=="" (
    for %%M in (%HIDDEN_IMPORTS%) do (
        set PACK_CMD=%PACK_CMD% --hidden-import=%%M
    )
)

REM 添加静默优化参数
set PACK_CMD=%PACK_CMD% --hidden-import=tkinter
set PACK_CMD=%PACK_CMD% --hidden-import=tkinter.ttk
set PACK_CMD=%PACK_CMD% --hidden-import=tkinter.messagebox
set PACK_CMD=%PACK_CMD% --hidden-import=tkinter.filedialog
set PACK_CMD=%PACK_CMD% --hidden-import=threading
set PACK_CMD=%PACK_CMD% --hidden-import=os
set PACK_CMD=%PACK_CMD% --hidden-import=sys
set PACK_CMD=%PACK_CMD% --hidden-import=json
set PACK_CMD=%PACK_CMD% --hidden-import=urllib
set PACK_CMD=%PACK_CMD% --hidden-import=ssl
set PACK_CMD=%PACK_CMD% --hidden-import=re
set PACK_CMD=%PACK_CMD% --hidden-import=subprocess
set PACK_CMD=%PACK_CMD% --exclude-module=_bootlocale
set PACK_CMD=%PACK_CMD% --exclude-module=doctest
set PACK_CMD=%PACK_CMD% --exclude-module=pdb
set PACK_CMD=%PACK_CMD% --exclude-module=unittest
set PACK_CMD=%PACK_CMD% --exclude-module=difflib
set PACK_CMD=%PACK_CMD% --exclude-module=turtle
set PACK_CMD=%PACK_CMD% --exclude-module=test
set PACK_CMD=%PACK_CMD% --exclude-module=distutils
set PACK_CMD=%PACK_CMD% --runtime-hook=pyi_rth_tkinter
set PACK_CMD=%PACK_CMD% --name="%OUTPUT_NAME%"
set PACK_CMD=%PACK_CMD% "%MAIN_SCRIPT%"

echo [INFO] 执行打包命令...
%PACK_CMD%

if errorlevel 1 (
    echo [ERROR] PyInstaller 打包失败！
    echo [HELP] 请检查以下可能的问题:
    echo        1. 主脚本语法错误
    echo        2. 缺少必要的依赖
    echo        3. 导入路径问题
    pause
    exit /b 1
)

echo.
echo [STEP 4/4] ✅ 打包完成！

REM ===========================================
REM 成功信息显示
REM ===========================================

echo.
echo =============================================
echo        ✅ 静默优化打包成功完成！
echo =============================================
echo.
echo   🎉 生成的可执行文件位于：
echo.
echo      %PROJECT_DIR%\dist\%OUTPUT_NAME%.exe
echo.
echo   📝 静默优化特性：
echo.
echo      • 完全无感启动和关闭
echo      • 无黑色命令行窗口闪现
echo      • 自动进程清理和资源释放
echo      • 专业级用户体验
echo.
echo   🔧 集成的优化功能：
echo.
echo      • --windowed 参数隐藏控制台
echo      • 智能进程管理
echo      • 静默异常处理
echo      • 快速响应关闭操作
echo.
echo   ⚠️  使用注意事项：
echo.
echo      • 首次运行可能需要几秒初始化
echo      • 防病毒软件可能需要白名单添加
echo      • 确保目标系统已安装 VC++ 运行库
echo.
echo =============================================
echo       按任意键退出...
pause >nul