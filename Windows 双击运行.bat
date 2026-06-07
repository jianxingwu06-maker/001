@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ========================================
echo 链接转店小秘成品表格自动化系统
echo ========================================
echo.
echo [信息] 当前目录：%cd%
echo [信息] input 目录内容：
dir input
echo.

if not exist "input\links.txt" (
  echo [错误] 未找到 input\links.txt，请先创建商品链接输入文件。
  pause
  exit /b 1
)

if not exist "input\template.xlsx" (
  echo [错误] 未找到 input\template.xlsx，请把店小秘 Excel 模板放到 input 目录。
  echo [错误] 完整路径：%cd%\input\template.xlsx
  pause
  exit /b 1
)

python --version >nul 2>&1
if errorlevel 1 (
  py --version >nul 2>&1
  if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10 或更高版本。
    pause
    exit /b 1
  )
  set "PYTHON_CMD=py"
) else (
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [信息] 正在创建虚拟环境 .venv ...
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 (
    echo [错误] 虚拟环境创建失败。
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"

echo [信息] 正在安装/更新本项目依赖 ...
python -m pip install --upgrade pip
python -m pip install -e .
if errorlevel 1 (
  echo [错误] 依赖安装失败。
  pause
  exit /b 1
)

echo [信息] 开始生成店小秘 Excel 和报告 ...
dxm-link-builder --links "input\links.txt" --template "input\template.xlsx" --output "output" --platform "default" --accounts "account_1"
if errorlevel 1 (
  echo.
  echo [提示] 如果看到 Excel 无法打开或未找到表头，请确认 input\template.xlsx 已被替换为真实店小秘 Excel 模板。
  pause
  exit /b 1
)

echo.
echo [完成] 结果已输出到 output 目录。
pause
