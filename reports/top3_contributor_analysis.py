import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# ---------------------- 核心配置：柔和莫兰迪色系（完整英文类型+固定颜色） ----------------------
TYPE_COLOR_MAP = {
    'Merge PR': '#E8C4C4',
    'Dependency': '#C4C4E8',
    'Release': '#E8E0C4',
    'Bug Fix': '#C4D6E8',
    'Feature': '#D4E8C4',
    'Refactor': '#D4C4E8',
    'Docs': '#C4E8E8',
    'Test': '#E8C4E0',
    'Maintenance': '#E8D4C4',
    'Other': '#D0D0D0'
}

# ---------------------- 1. 数据读取与处理 ----------------------
csv_path = "top3_contributor_analysis.csv"  # 替换为你的CSV路径
df = pd.read_csv(csv_path)

# 校验必要列
required_cols = ['时间范围', '贡献者', '提交类型', '该类型提交数']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise ValueError(f"CSV缺少列：{missing_cols}")

# 目标时间范围
target_time_ranges = ['全时段', '近5年', '近2年']
df = df[df['时间范围'].isin(target_time_ranges)]
if df.empty:
    raise ValueError("无目标时间范围的数据")

# 校验提交类型是否在预设中，去除空格避免匹配失败
df['提交类型'] = df['提交类型'].str.strip()
unknown_types = df[~df['提交类型'].isin(TYPE_COLOR_MAP.keys())]['提交类型'].unique()
if len(unknown_types) > 0:
    raise ValueError(f"存在未预设颜色的提交类型：{unknown_types}")

# ---------------------- 2. 按时间范围生成图表 ----------------------
for time_range in target_time_ranges:
    df_time = df[df['时间范围'] == time_range]
    if df_time.empty:
        print(f"⚠️ {time_range} 无数据，跳过")
        continue
    
    # 取当前时间范围Top3贡献者
    top3_contributors = df_time.groupby('贡献者')['该类型提交数'].sum().nlargest(3).index.tolist()
    if len(top3_contributors) < 3:
        print(f"⚠️ {time_range} 仅找到{len(top3_contributors)}个贡献者，不足3个")
        continue
    
    # 创建画布
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    fig.suptitle(f'贡献者提交类型分布 - {time_range}', fontsize=20, y=0.98, fontweight='bold')
    
    for idx, contributor in enumerate(top3_contributors):
        ax = axes[idx]
        df_contributor = df_time[df_time['贡献者'] == contributor]
        
        # 聚合提交类型（不合并任何类型），按提交数降序
        commit_stats = df_contributor.groupby('提交类型')['该类型提交数'].sum().sort_values(ascending=False)
        commit_stats = commit_stats[commit_stats > 0]  # 仅保留提交数>0的类型
        total = commit_stats.sum()
        
        # 获取颜色列表（所有类型都有独立颜色）
        pie_colors = [TYPE_COLOR_MAP[type_name] for type_name in commit_stats.index]
        
        # 自定义标签：占比≥3%显示类型名，<3%显示空字符串（仅隐藏文字）
        def get_labels():
            labels = []
            for type_name, count in commit_stats.items():
                pct = count / total * 100
                labels.append(type_name if pct >= 3 else '')
            return labels
        
        labels = get_labels()
        
        # 绘制饼图（保留所有类型，仅隐藏占比<3%的标签）
        wedges, texts, autotexts = ax.pie(
            commit_stats.values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 12, 'wrap': True},
            labeldistance=1.1,
            pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            colors=pie_colors,
            rotatelabels=False,
        )
        
        # 优化标签显示
        for text in texts:
            text.set_rotation(0)
            text.set_ha('center')
            text.set_wrap(True)
            pos = text.get_position()
            text.set_position((pos[0], pos[1] + 0.05))
        
        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('#333333')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
            autotext.set_ha('center')
        
        # 标题配置
        ax.set_title(contributor, fontsize=16, pad=30, fontweight='bold', y=-0.15)
        ax.set_aspect('equal')
    
    # 调整布局防重叠
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    # 保存图片（英文命名更规范）
    save_name = f'contributor_commit_analysis_{time_range}.png'
    plt.savefig(save_name, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ {time_range} 图表已保存：{save_name}")

print("\n🎉 图表生成完成！")