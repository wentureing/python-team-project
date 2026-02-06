# -*- coding: utf-8 -*-
"""
设计模式分析辅助工具
核心功能：
1. 提取requests项目核心模块的类和方法结构
2. 生成类-方法调用关系文档
3. 标记可能涉及的设计模式（如工厂模式、单例模式）
作者：lemenpop
日期：2026
"""

import os
from pathlib import Path

class DesignPatternHelper:
    """设计模式分析辅助类"""
    def __init__(self, project_root=None):
        """
        初始化：指定requests项目根路径（后续替换为真实路径）
        :param project_root: requests项目本地路径
        """
        # 示例：假设requests项目克隆到本地data文件夹（后续可修改为真实路径）
        self.project_root = project_root or '../data/requests'
        # requests核心模块（重点分析这些文件）
        self.core_modules = [
            'requests/api.py',
            'requests/sessions.py',
            'requests/models.py',
            'requests/adapters.py',
            'requests/auth.py'
        ]

    def extract_class_methods(self, file_path):
        """
        提取单个Python文件中的类和方法
        :param file_path: Python文件路径
        :return: 类-方法字典
        """
        if not os.path.exists(file_path):
            return {}
        
        class_methods = {}
        current_class = None
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                # 匹配类定义（class XXX: 或 class XXX(Parent):）
                if line.startswith('class ') and (line.endswith(':') or '(' in line):
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    current_class = class_name
                    class_methods[current_class] = []
                # 匹配方法定义（def XXX(self, ...):）
                elif line.startswith('def ') and 'self' in line and line.endswith(':'):
                    if current_class:
                        method_name = line.split('def ')[1].split('(')[0].strip()
                        class_methods[current_class].append((method_name, line_num))  # 记录方法名和行号
        return class_methods

    def generate_structure_report(self):
        """生成核心模块的类-方法结构报告"""
        report = []
        report.append("# Requests项目核心代码结构报告（设计模式分析用）")
        report.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*50 + "\n")

        for module in self.core_modules:
            module_path = Path(self.project_root) / module
            if not module_path.exists():
                report.append(f"模块不存在：{module}")
                report.append("")
                continue
            
            report.append(f"## 模块：{module}")
            class_methods = self.extract_class_methods(module_path)
            
            if not class_methods:
                report.append("  无公开类定义")
            else:
                for cls, methods in class_methods.items():
                    report.append(f"### 类：{cls}")
                    report.append("  方法列表（方法名：行号）：")
                    for method, line_num in methods:
                        report.append(f"    - {method}: 第{line_num}行")
                    # 标记可能的设计模式（基于类名/方法名推测）
                    pattern_hints = self._guess_design_pattern(cls, methods)
                    if pattern_hints:
                        report.append(f"  可能的设计模式：{', '.join(pattern_hints)}")
                    report.append("")
        
        # 保存报告到docs文件夹
        report_path = '../docs/design_pattern_structure.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"设计模式辅助报告已生成：{report_path}")
        print("报告包含：核心类-方法结构、设计模式推测")

    def _guess_design_pattern(self, class_name, methods):
        """
        基于类名和方法名推测可能的设计模式
        :return: 设计模式名称列表
        """
        hints = []
        method_names = [m[0] for m in methods]
        
        # 单例模式：有 get_instance() 或 __new__ 方法
        if 'get_instance' in method_names or '__new__' in method_names:
            hints.append('单例模式')
        # 工厂模式：类名含 Factory 或有 create_xxx 方法
        if 'Factory' in class_name or any(m.startswith('create_') for m in method_names):
            hints.append('工厂模式')
        # 适配器模式：类名含 Adapter 或有 adapt 方法
        if 'Adapter' in class_name or 'adapt' in method_names:
            hints.append('适配器模式')
        # 策略模式：类名含 Strategy 或有 set_strategy 方法
        if 'Strategy' in class_name or 'set_strategy' in method_names:
            hints.append('策略模式')
        
        return hints

# 主函数：运行生成报告
if __name__ == "__main__":
    helper = DesignPatternHelper()
    helper.generate_structure_report()
    print("\n设计模式辅助分析完成")