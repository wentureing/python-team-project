import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 中文显示配置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# ---------------------- 核心配置：柔和莫兰迪色系 ----------------------
# 为每个提交类型分配柔和RGB颜色，确保视觉舒适且区分度足够
TYPE_COLOR_MAP = {
    '代码提交': '#E8C4C4',
    '文档更新': '#C4E8E8',
    'Bug修复': '#C4D6E8',
    '功能新增': '#D4E8C4',
    '测试用例': '#E8E0C4',
    '配置修改': '#E8C4E0',
    '依赖更新': '#C4C4E8',
    '重构': '#D4C4E8',
    '其他': '#D0D0D0'
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

# 获取所有唯一提交类型，确保颜色覆盖所有类型
all_types = df['提交类型'].unique()
default_colors = ['#E8D4C4', '#D4E8C4', '#C4E8D4', '#C4D4E8', '#D4C4E8', '#E8C4D4']  # 柔和默认色
for idx, type_name in enumerate(all_types):
    if type_name not in TYPE_COLOR_MAP:
        TYPE_COLOR_MAP[type_name] = default_colors[idx % len(default_colors)]

# ---------------------- 2. 按时间范围生成图表 ----------------------
for time_range in target_time_ranges:
    # 筛选当前时间范围的所有数据
    df_time = df[df['时间范围'] == time_range]
    if df_time.empty:
        print(f"⚠️ {time_range} 无数据，跳过")
        continue
    
    # 按当前时间范围单独取Top3贡献者（每个时段贡献者独立）
    top3_contributors = df_time.groupby('贡献者')['该类型提交数'].sum().nlargest(3).index.tolist()
    if len(top3_contributors) < 3:
        print(f"⚠️ {time_range} 仅找到{len(top3_contributors)}个贡献者，不足3个")
        continue
    
    # 创建画布：1行3列子图，适配长名称
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    fig.suptitle(f'贡献者提交类型分布 - {time_range}', fontsize=20, y=0.98, fontweight='bold')

    # 遍历每个贡献者绘制子图
    for idx, contributor in enumerate(top3_contributors):
        ax = axes[idx]
        # 筛选当前贡献者在该时间范围的提交数据
        df_contributor = df_time[df_time['贡献者'] == contributor]
        if df_contributor.empty:
            ax.text(0.5, 0.5, '无提交数据', ha='center', va='center', fontsize=18, fontweight='bold')
            ax.set_title(contributor, fontsize=16, pad=20, fontweight='bold', y=-0.1)  # 标题移到下方
            ax.axis('off')
            continue
        
        # 聚合提交类型 + 按提交数降序排序
        commit_stats = df_contributor.groupby('提交类型')['该类型提交数'].sum().sort_values(ascending=False)
        commit_stats = commit_stats[commit_stats > 0]
        
        # 计算百分比，筛选出占比≥3%的类型
        total = commit_stats.sum()
        commit_stats_filtered = commit_stats[commit_stats / total >= 0.03]
        # 处理占比<3%的部分（合并为"其他"）
        if len(commit_stats) != len(commit_stats_filtered):
            other_sum = commit_stats[commit_stats / total < 0.03].sum()
            commit_stats_filtered['其他（<3%）'] = other_sum
        
        # 获取当前饼图的类型颜色列表（匹配柔和颜色）
        pie_colors = [TYPE_COLOR_MAP.get(type_name, '#D0D0D0') for type_name in commit_stats_filtered.index]
        
        # 自定义标签生成函数（仅显示名称，百分比在autopct中）
        def make_labels(sizes):
            labels = []
            for size in sizes:
                pct = size / total * 100
                if pct >= 3:
                    labels.append(f'{commit_stats_filtered.index[list(sizes).index(size)]}')
                else:
                    labels.append('')  # 占比<3%不显示名称
            return labels
        
        # 绘制饼图（优化标签显示）
        wedges, texts, autotexts = ax.pie(
            commit_stats_filtered.values,
            labels=make_labels(commit_stats_filtered.values),  # 仅显示≥3%的名称
            autopct='%1.1f%%',
            startangle=90,  # 从正上方开始，大区块自动到左上方
            textprops={'fontsize': 12, 'wrap': True},
            labeldistance=1.1,  # 标签距离饼图稍远，防重叠
            pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2},
            colors=pie_colors,  # 使用柔和颜色
            rotatelabels=False,  # 关闭标签旋转，强制横向显示
        )
        
        # ---------------------- 优化标签显示：横向+防重叠 ----------------------
        # 调整标签位置，确保横向且不重叠
        for text in texts:
            text.set_rotation(0)  # 强制标签横向显示
            text.set_ha('center')  # 水平居中
            text.set_wrap(True)    # 自动换行（长名称）
            # 微调标签y轴位置，避免重叠
            pos = text.get_position()
            text.set_position((pos[0], pos[1] + 0.05))
        
        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('#333333')  # 深灰色替代白色，更柔和
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
            autotext.set_ha('center')  # 百分比文字居中
        
        # 标题移到饼图下方，增加与饼图的间距
        ax.set_title(contributor, fontsize=16, pad=30, fontweight='bold', y=-0.15)
        ax.set_aspect('equal')  # 正圆

    # 调整布局防重叠（增加底部间距）
    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    # 保存高清图片
    save_name = f'贡献者提交分析_{time_range}.png'
    plt.savefig(save_name, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ {time_range} 图表已保存：{save_name}")

print("\n🎉 图表生成完成！")