@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion

title 链接转店小秘成品表格自动化系统

set "ROOT_DIR=%~dp0"
set "INPUT_DIR=%ROOT_DIR%input"
set "OUTPUT_DIR=%ROOT_DIR%output"
set "LINKS_FILE=%INPUT_DIR%\links.txt"
set "TEMPLATE_FILE=%INPUT_DIR%\template.xlsx"
set "VENV_DIR=%ROOT_DIR%.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PYTHONUTF8=1"
set "PYTHONPATH=%ROOT_DIR%src"

if not exist "%INPUT_DIR%" mkdir "%INPUT_DIR%"
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"
if not exist "%OUTPUT_DIR%\images" mkdir "%OUTPUT_DIR%\images"
if not exist "%OUTPUT_DIR%\reports" mkdir "%OUTPUT_DIR%\reports"

echo.
echo ================================================
echo   链接转店小秘成品表格 - Windows 双击运行版
echo ================================================
echo.

if not exist "%LINKS_FILE%" (
    echo 【缺少文件】没有找到 input\links.txt
    echo.
    echo 请在项目根目录的 input 文件夹里新建 links.txt，
    echo 然后把商品链接逐行复制进去：一行一个链接。
    echo.
    explorer "%INPUT_DIR%"
    pause
    exit /b 1
)

if not exist "%TEMPLATE_FILE%" (
    echo 【缺少文件】没有找到 input\template.xlsx
    echo.
    echo 请把店小秘导出的 Excel 模板文件放到 input 文件夹，
    echo 并命名为 template.xlsx。
    echo.
    explorer "%INPUT_DIR%"
    pause
    exit /b 1
)

set "BASE_PY="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "BASE_PY=py -3"
)

if not defined BASE_PY (
    where python >nul 2>nul
    if not errorlevel 1 (
        python --version >nul 2>nul
        if not errorlevel 1 set "BASE_PY=python"
    )
)

if not defined BASE_PY (
    echo 【缺少 Python】这台电脑没有检测到可用的 Python。
    echo.
    echo 请先安装 Python 3.10 或更高版本：
    echo https://www.python.org/downloads/windows/
    echo.
    echo 安装时请务必勾选：Add python.exe to PATH
    echo 安装完成后，重新双击本文件运行。
    echo.
    pause
    exit /b 1
)

echo 正在检查运行环境，请稍等...
if not exist "%VENV_PY%" (
    echo 第一次运行：正在创建本项目专用 Python 环境...
    %BASE_PY% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo 【环境创建失败】无法创建 .venv 环境。
        echo 请确认 Python 安装完整，并且安装时勾选了 Add python.exe to PATH。
        pause
        exit /b 1
    )
)

echo 正在自动安装/检查依赖库...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r "%ROOT_DIR%requirements.txt"
if errorlevel 1 (
    echo.
    echo 【依赖安装失败】依赖库没有安装成功。
    echo 请检查当前电脑是否能访问网络，或公司网络是否拦截了 pip 下载。
    echo 如果仍失败，请把本窗口截图发给技术人员。
    echo.
    pause
    exit /b 1
)

echo.
echo 正在采集链接、合规重构、处理图片并生成店小秘表格...
"%VENV_PY%" -m dxm_link_builder.cli ^
    --links "%LINKS_FILE%" ^
    --template "%TEMPLATE_FILE%" ^
    --output "%OUTPUT_DIR%" ^
    --platform default ^
    --accounts account_1

if errorlevel 1 (
    echo.
    echo 【运行失败】程序没有成功生成表格。
    echo 请检查 input\links.txt 是否为一行一个商品链接，template.xlsx 是否为店小秘模板。
    echo 详细问题可查看 output\reports 文件夹；如果没有报告，请把本窗口截图发给技术人员。
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   处理完成！
echo   主文件：output\店小秘可上传成品表格.xlsx
echo   图片：output\images
echo   报告：output\reports
echo ================================================
echo.
start "" "%OUTPUT_DIR%"
pause
exit /b 0
