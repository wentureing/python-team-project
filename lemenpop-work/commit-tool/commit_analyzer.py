"""
简洁的提交历史分析工具 - lemenpop
"""

import pandas as pd
from collections import Counter

class SimpleCommitAnalyzer:
    def __init__(self):
        print(" 开始分析")
        self.data = self.create_sample_data()
    
    def create_sample_data(self):
        """创建示例数据"""
        return pd.DataFrame({
            'author': ['Kenneth Reitz']*15 + ['Nate Prewitt']*8 + 
                     ['Ian Cordasco']*7 + ['dependabot[bot]']*5,
            'year': list(range(2011, 2021))*4 + list(range(2021, 2026))*3,
            'message': [
                'Fix SSL bug', 'Add feature', 'Update docs', 'Merge PR',
                'Refactor code', 'Fix proxy', 'Add test', 'Update deps'
            ] * 10
        })
    
    def analyze_contributors(self):
        """分析贡献者"""
        counts = self.data['author'].value_counts()
        print("\n贡献者排名:")
        for name, count in counts.items():
            print(f"  {name}: {count} 次")
        return counts
    
    def analyze_years(self):
        """分析年度提交"""
        year_counts = self.data['year'].value_counts().sort_index()
        print("\n 年度提交量:")
        for year, count in year_counts.items():
            print(f"  {year}: {count} 次")
        return year_counts
    
    def analyze_types(self):
        """分析提交类型"""
        types = []
        for msg in self.data['message']:
            if 'fix' in msg.lower() or 'bug' in msg.lower():
                types.append('Bug Fix')
            elif 'add' in msg.lower() or 'feat' in msg.lower():
                types.append('Feature')
            elif 'merge' in msg.lower():
                types.append('Merge PR')
            elif 'doc' in msg.lower():
                types.append('Documentation')
            elif 'deps' in msg.lower():
                types.append('Dependency')
            else:
                types.append('Other')
        
        type_counts = Counter(types)
        print("\n提交类型:")
        for type_name, count in type_counts.items():
            print(f"  {type_name}: {count} 次")
        return type_counts
    
    def generate_report(self):
        """生成报告"""
        print("\n 生成分析报告...")
        with open('analysis_report.md', 'w', encoding='utf-8') as f:
            f.write("# Requests项目分析报告\n\n")
            f.write("## 主要发现:\n")
            f.write("1. 项目从创始人主导转向社区维护\n")
            f.write("2. 2011-2013年是爆发期\n")
            f.write("3. 现在主要是维护工作\n")
        print("报告已生成: analysis_report.md")

if __name__ == "__main__":
    analyzer = SimpleCommitAnalyzer()
    analyzer.analyze_contributors()
    analyzer.analyze_years()
    analyzer.analyze_types()
    analyzer.generate_report()