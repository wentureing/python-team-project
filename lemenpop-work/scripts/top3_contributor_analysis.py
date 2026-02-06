# -*- coding: utf-8 -*-
"""
Top3贡献者提交类型分析工具（最终运行版）
核心功能：全时段/近5年/近2年Top3提交者类型统计
作者：lemenpop
日期：2026
"""

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta  # 已确保导入
from collections import Counter
from analyze_commits_v2 import CommitAnalyzer  # 复用修复后的父类
import os

class Top3ContributorAnalyzer(CommitAnalyzer):
    """继承后直接使用'commit_type'列，无KeyError"""
    def __init__(self):
      super().__init__()  # 父类已无参数，直接调用

    def _get_time_filtered_data(self, time_range):
        """时间范围筛选（全时段/5年/2年）"""
        now = datetime.now()
        if time_range == '5y':
            start_date = now - relativedelta(years=5)
            return self.df[self.df['date'] >= start_date]
        elif time_range == '2y':
            start_date = now - relativedelta(years=2)
            return self.df[self.df['date'] >= start_date]
        else:  # all 全时段
            return self.df.copy()

    def get_top3_contributors(self, time_range='all'):
        """获取指定时间范围Top3提交者"""
        filtered_df = self._get_time_filtered_data(time_range)
        return filtered_df['author'].value_counts().head(3).index.tolist()

    def analyze_top3_commit_types(self, time_range='all'):
        """分析Top3提交者的提交类型分布"""
        filtered_df = self._get_time_filtered_data(time_range)
        top3_authors = self.get_top3_contributors(time_range)
        results = {}

        print(f"\n" + "="*60)
        print(f" {time_range.upper()} 时间范围 - Top3贡献者提交类型分析")
        print("="*60)

        for author in top3_authors:
            author_commits = filtered_df[filtered_df['author'] == author]
            type_counts = Counter(author_commits['commit_type'])  # 现在有commit_type列了
            total = len(author_commits)
            results[author] = {'总提交数': total, '提交类型分布': dict(type_counts)}

            # 打印结果（清晰易读）
            print(f"\n【{author}】")
            print(f"提交总数：{total} 条")
            print("提交类型分布：")
            for commit_type, count in type_counts.most_common():
                print(f"  - {commit_type}: {count} 条 ({(count/total*100):.1f}%)")

        return results

    def run_all_time_ranges(self):
        """一键运行所有时间范围分析+保存结果"""
        time_ranges = ['all', '5y', '2y']
        all_results = {}

        # 分析所有时间范围
        for tr in time_ranges:
            all_results[tr] = self.analyze_top3_commit_types(tr)

        # 自动创建reports目录并保存结果
        reports_dir = '../reports'
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        self._save_results_to_csv(all_results, reports_dir)
        print(f"\n所有分析结果已保存到：{os.path.join(reports_dir, 'top3_contributor_analysis.csv')}")

    def _save_results_to_csv(self, all_results, reports_dir):
        """结果保存为CSV"""
        rows = []
        for time_range, author_results in all_results.items():
            for author, result in author_results.items():
                total = result['总提交数']
                for commit_type, count in result['提交类型分布'].items():
                    rows.append({
                        '时间范围': {'all': '全时段', '5y': '近5年', '2y': '近2年'}[time_range],
                        '贡献者': author,
                        '总提交数': total,
                        '提交类型': commit_type,
                        '该类型提交数': count,
                        '占比(%)': round(count/total*100, 1)
                    })
        pd.DataFrame(rows).to_csv(
            os.path.join(reports_dir, 'top3_contributor_analysis.csv'),
            index=False, encoding='utf-8'
        )

if __name__ == "__main__":
    top3_analyzer = Top3ContributorAnalyzer()
    top3_analyzer.run_all_time_ranges()
    print("\n" + "="*50)
    print("所有分析完成")
    print("="*50)