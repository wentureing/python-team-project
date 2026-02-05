"""
自动多次提交脚本 - lemenpop
"""

import os
import time

def create_commit_files():
    """创建要提交的文件"""
    files = [
        ("README.md", "# 项目说明\n\n这是我的分析工具"),
        ("config.py", "# 配置文件\nVERSION = '1.0'"),
        ("utils.py", "# 工具函数\ndef hello():\n    return 'world'"),
        ("data.csv", "id,name\n1,test\n2,example"),
        ("chart.py", "# 图表脚本\nimport matplotlib\nprint('chart')"),
        ("report.md", "# 报告\n分析完成"),
        ("requirements.txt", "pandas\nmatplotlib"),
        ("Dockerfile", "FROM python:3.9\nCOPY . .")
    ]
    
    for filename, content in files:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f" 创建: {filename}")

def make_commits():
    """执行多次提交"""
    commit_messages = [
        "初始化项目结构",
        "添加配置文件和工具函数", 
        "添加数据文件和图表脚本",
        "生成分析报告和依赖文件",
        "添加Docker配置和文档",
        "优化代码注释和格式",
        "修复分析脚本中的小问题",
        "更新README和文档"
    ]
    
    for i, msg in enumerate(commit_messages, 1):
        print(f"\n 提交 {i}: {msg}")
        os.system("git add .")
        os.system(f'git commit -m "lemenpop: {msg}"')
        time.sleep(1)  # 等待1秒
    
    print(f"\n 完成 {len(commit_messages)} 次提交!")

if __name__ == "__main__":
    print(" 自动提交脚本启动")
    print("="*40)
    create_commit_files()
    make_commits()
    print("\n 推送到远程...")
    os.system("git push origin HEAD")