@echo off
chcp 65001 > nul
echo.
echo ================================
echo   傻瓜式提交工具 - lemenpop
echo ================================
echo.

echo 第一步: 检查Python
python --version
if errorlevel 1 (
    echo 错误: 请先安装Python
    pause
    exit
)

echo.
echo 第二步: 创建分析脚本
python -c "print('创建分析脚本...')"
copy nul simple_analyzer.py >nul
echo ✅ 创建成功

echo.
echo 第三步: 运行自动提交
echo 注意: 这需要Git已经初始化
echo.
echo 按任意键开始自动提交...
pause >nul

python auto_committer.py

echo.
echo ================================
echo    完成！
echo ================================
echo.
echo 生成的提交:
git log --oneline -10
echo.
echo 生成的文件:
dir /B
echo.
pause