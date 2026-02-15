# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter

class CommitAnalyzer:
    """提交记录分析核心类（适配git log导出的无表头CSV）"""
    # 直接指定真实数据路径，无需外部传参
    def __init__(self):
        """初始化：自动加载真实数据+字段映射+类型分类，无任何外部依赖"""
        self.data_path = r"C:\Users\dell\my-course-work\python-team-project\requests_commits.csv"
     
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(
                self.data_path,
                encoding='utf-8-sig',       # 解决UTF-8带BOM编码问题
                quotechar='"',             # 正确解析含逗号的提交说明
                on_bad_lines='skip',       # 新版Pandas唯一有效：跳过格式错误行
                header=None,               # 关键：git log导出的CSV无表头
                names=['commit_id', 'author', 'date', 'message']  # 手动映射列名（必须和git log列顺序一致）
            )
            print(f"成功加载真实数据：{self.data_path}（共{len(self.df)}条提交记录）")
        else:
            self._create_sample_data()  # 备用：真实数据不存在时生成示例
        
       
        self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce', utc=True).dt.tz_localize(None)
        # 过滤掉日期转换失败的无效行
        self.df = self.df.dropna(subset=['date'])
        
        # 提交类型分类规则（和组长保持一致的10类）
        self.commit_type_rules = [
            ('Merge PR', ['merge', 'pr']),
            ('Dependency', ['dependency', 'update package', 'pip', 'requirements']),
            ('Release', ['release', 'v\\d+\\.', 'version']),
            ('Bug Fix', ['fix', 'bug', 'repair', 'correct']),
            ('Feature', ['add', 'new', 'feature', 'implement']),
            ('Refactor', ['refactor', 'restructure', 'optimize']),
            ('Docs', ['doc', 'documentation', 'readme', '说明']),
            ('Test', ['test', 'pytest', 'unit test', 'ci']),
            ('Maintenance', ['maintain', 'clean', 'format', 'lint']),
            ('Other', [])
        ]
        
        # 自动添加提交类型列（子类直接可用，无KeyError）
        self.df['commit_type'] = self.df['message'].apply(self.classify_commit_type)

    def _create_sample_data(self):
        """备用：真实数据不存在时生成示例数据"""
        data_dir = '../data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        sample_data = {
            'commit_id': list(range(1, 51)),
            'message': ['fix: 修复bug', 'feat: 新增功能', 'docs: 更新文档'] * 17,
            'author': ['Kenneth Reitz', 'dependabot[bot]', 'Nate Prewitt'] * 17,
            'date': pd.date_range(start='2019-01-01', periods=50, freq='ME')
        }
        self.df = pd.DataFrame(sample_data)
        sample_path = os.path.join(data_dir, 'sample_commits.csv')
        self.df.to_csv(sample_path, index=False, encoding='utf-8')
        print(f" 真实数据不存在，生成示例数据：{sample_path}")

    def classify_commit_type(self, message):
        """提交类型自动分类"""
        if pd.isna(message):
            return 'Other'
        message = message.lower()
        for commit_type, keywords in self.commit_type_rules:
            if any(keyword in message for keyword in keywords):
                return commit_type
        return 'Other'

    def basic_statistics(self):
        """基础统计输出"""
        print("\n" + "="*50)
        print(" requests项目提交记录基础统计")
        print("="*50)
        print(f"有效提交数：{len(self.df)} 条")
        print(f"贡献者数量：{self.df['author'].nunique()} 人")
        print(f"时间范围：{self.df['date'].min().strftime('%Y-%m-%d')} ~ {self.df['date'].max().strftime('%Y-%m-%d')}")
        print("="*50 + "\n")

if __name__ == "__main__":
    # 单独运行测试
    analyzer = CommitAnalyzer()
    analyzer.basic_statistics()
    # 自动创建reports目录并保存数据
    reports_dir = '../reports'
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    analyzer.df.to_csv(os.path.join(reports_dir, 'real_commits_with_type.csv'), index=False, encoding='utf-8')
    print(f" 带类型的真实数据已保存：{reports_dir}/real_commits_with_type.csv")