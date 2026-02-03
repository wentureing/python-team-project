import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path
from datetime import datetime

# 配置文件路径和输出目录
file_path = "requests_commits.csv"
output_dir = Path("analyze_commits_figures")
output_dir.mkdir(exist_ok=True)

# 读取提交数据
commits = []
with open(file_path, "r", encoding="utf-8") as f:
    header = f.readline() 
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",", 3)
        if len(parts) < 4:
            continue
        commits.append({
            "author": parts[1].strip(),
            "time": parts[2].strip(),
            "message": parts[3].strip()
        })

# -------------------------- 封装可复用函数 --------------------------
def plot_top_contributors(commits_data, title, save_name):
    """绘制Top10贡献者柱状图"""
    author_counter = Counter(c["author"] for c in commits_data)
    top_authors = author_counter.most_common(10)
    if not top_authors:  # 处理空数据
        print(f"警告：{title} 无数据可展示")
        return
    
    authors = [a for a, _ in top_authors]
    author_counts = [c for _, c in top_authors]

    plt.figure()
    bars = plt.bar(authors, author_counts)
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Author")
    plt.ylabel("Number of Commits")
    plt.title(title)
    for bar, count in zip(bars, author_counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                 str(count), ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir/save_name, dpi=300)
    plt.close()

def analyze_commit_types(commits_data):
    """分析提交类型并返回类型列表和对应数量"""
    merge = dependency = bugfix = feature = 0
    refactor = docs = test = release = maintenance = other = 0

    for c in commits_data:
        msg = c["message"].lower()
        if msg.startswith("merge pull request"):
            merge += 1
        elif "bump" in msg or "dependabot" in msg:
            dependency += 1
        elif "release" in msg or msg.startswith("v"):
            release += 1
        elif "fix" in msg or "bug" in msg or "error" in msg:
            bugfix += 1
        elif "add" in msg or "feature" in msg or "support" in msg or "implement" in msg:
            feature += 1
        elif "refactor" in msg or "cleanup" in msg or "restructure" in msg:
            refactor += 1
        elif "doc" in msg or "docs" in msg or "readme" in msg:
            docs += 1
        elif "test" in msg or "ci" in msg or "workflow" in msg:
            test += 1
        elif any(k in msg for k in [
            "update", "improve", "change", "adjust", "remove",
            "minor", "tweak", "simplify", "optimize", "handle", "use"
        ]):
            maintenance += 1
        else:
            other += 1

    types = [
        "Merge PR", "Dependency", "Release", "Bug Fix", "Feature",
        "Refactor", "Docs", "Test", "Maintenance", "Other"
    ]
    type_counts = [merge, dependency, release, bugfix, feature,
                   refactor, docs, test, maintenance, other]
    return types, type_counts

def plot_commit_types(commits_data, title, save_name):
    """绘制提交类型分布柱状图"""
    types, type_counts = analyze_commit_types(commits_data)
    if sum(type_counts) == 0:  # 处理空数据
        print(f"警告：{title} 无数据可展示")
        return
    
    plt.figure()
    bars = plt.bar(types, type_counts)
    plt.xlabel("Commit Type")
    plt.ylabel("Number of Commits")
    plt.title(title)
    plt.xticks(rotation=30, ha="right")
    for bar, count in zip(bars, type_counts):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                 str(count), ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir/save_name, dpi=300)
    plt.close()

# -------------------------- 原有功能 --------------------------
# 1. 全部数据 - Top10贡献者
plot_top_contributors(
    commits,
    title="Top 10 Contributors by Commit Count (All Time)",
    save_name="top_10_contributors.png"
)

# 2. 全部数据 - 提交类型分布
plot_commit_types(
    commits,
    title="Fine-grained Commit Type Distribution (All Time)",
    save_name="commit_type.png"
)

# 3. 年度提交统计
yearly_counter = Counter()
for c in commits:
    year = c["time"][:4]
    yearly_counter[year] += 1

years = sorted(yearly_counter.keys())
year_counts = [yearly_counter[y] for y in years]

plt.figure()
plt.plot(years, year_counts, marker="o")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Year")
plt.ylabel("Number of Commits")
plt.title("Yearly Commit Activity (All Time)")
for i, (x, y) in enumerate(zip(years, year_counts)):
    plt.text(x, y + 10.5, str(y), ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(output_dir/"yearly_commit.png", dpi=300)
plt.close()

# -------------------------- 新增：近五年/近两年数据分析 --------------------------
# 提取所有提交的年份
for c in commits:
    # 确保时间格式有效（兼容常见的YYYY-MM-DD等格式）
    try:
        c["year_int"] = int(c["time"][:4])
    except (ValueError, IndexError):
        c["year_int"] = None

# 过滤掉无效年份的数据
valid_commits = [c for c in commits if c["year_int"] is not None]
if not valid_commits:
    print("错误：无有效时间的提交数据，无法分析近五年/近两年数据")
else:
    # 获取最新年份
    latest_year = max(c["year_int"] for c in valid_commits)
    
    # 1. 近五年数据筛选（latest_year-4 ~ latest_year）
    five_years_range = range(latest_year - 4, latest_year + 1)
    five_years_commits = [c for c in valid_commits if c["year_int"] in five_years_range]
    
    # 2. 近两年数据筛选（latest_year-1 ~ latest_year）
    two_years_range = range(latest_year - 1, latest_year + 1)
    two_years_commits = [c for c in valid_commits if c["year_int"] in two_years_range]

    # -------------------------- 近五年分析 --------------------------
    # 近五年 - Top10贡献者
    plot_top_contributors(
        five_years_commits,
        title=f"Top 10 Contributors ({latest_year-4} - {latest_year})",
        save_name=f"top_10_contributors_5years.png"
    )
    
    # 近五年 - 提交类型分布
    plot_commit_types(
        five_years_commits,
        title=f"Commit Type Distribution ({latest_year-4} - {latest_year})",
        save_name=f"commit_type_5years.png"
    )

    # -------------------------- 近两年分析 --------------------------
    # 近两年 - Top10贡献者
    plot_top_contributors(
        two_years_commits,
        title=f"Top 10 Contributors ({latest_year-1} - {latest_year})",
        save_name=f"top_10_contributors_2years.png"
    )
    
    # 近两年 - 提交类型分布
    plot_commit_types(
        two_years_commits,
        title=f"Commit Type Distribution ({latest_year-1} - {latest_year})",
        save_name=f"commit_type_2years.png"
    )

print("分析完成！所有图表已保存至:", output_dir.absolute())