import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

file_path = "requests_commits.csv"

output_dir = Path("analyze_commits_figures")
output_dir.mkdir(exist_ok=True)

commits = []

# ================== 读取数据 ==================

with open(file_path, "r", encoding="utf-8") as f:
    header = f.readline()  # 跳过表头
    for line in f:
        line = line.strip()
        if not line:
            continue

        # 只分割前三个逗号
        parts = line.split(",", 3)
        if len(parts) < 4:
            continue

        commits.append({
            "author": parts[1].strip(),
            "time": parts[2].strip(),
            "message": parts[3].strip()
        })

# ================== 1. 作者提交次数（Top 10） ==================

author_counter = Counter(c["author"] for c in commits)
top_authors = author_counter.most_common(10)

authors = [a for a, _ in top_authors]
author_counts = [c for _, c in top_authors]

plt.figure()
bars = plt.bar(authors, author_counts)
plt.xticks(rotation=45, ha="right")
plt.xlabel("Author")
plt.ylabel("Number of Commits")
plt.title("Top 10 Contributors by Commit Count")
for bar, count in zip(bars, author_counts):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
             str(count), ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(output_dir/"top_10_contributors.png", dpi=300)
plt.close()

# ================== 2. 提交类型分布 ==================

merge_count = 0
bump_count = 0
fix_count = 0
other_count = 0

for c in commits:
    msg = c["message"].lower()
    if msg.startswith("merge pull request"):
        merge_count += 1
    elif msg.startswith("bump"):
        bump_count += 1
    elif "fix" in msg or "bug" in msg:
        fix_count += 1
    else:
        other_count += 1

types = ["Merge PR", "Dependency Bump", "Bug Fix", "Other"]
type_counts = [merge_count, bump_count, fix_count, other_count]

plt.figure()
bars = plt.bar(types, type_counts)
plt.xlabel("Commit Type")
plt.ylabel("Number of Commits")
plt.title("Commit Type Distribution")
for bar, count in zip(bars, type_counts):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
             str(count), ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(output_dir/"commit_type.png", dpi=300)
plt.close()

# ================== 3. 按月份提交统计 ==================

yearly_counter = Counter()

for c in commits:
    # 提取年份 YYYY
    year = c["time"][:4]
    yearly_counter[year] += 1

years = sorted(yearly_counter.keys())
year_counts = [yearly_counter[y] for y in years]

plt.figure()
plt.plot(years, year_counts, marker="o")
plt.xticks(rotation=45, ha="right")
plt.xlabel("Year")
plt.ylabel("Number of Commits")
plt.title("Yearly Commit Activity")
for i, (x, y) in enumerate(zip(years, year_counts)):
    plt.text(x, y + 10.5, str(y), ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(output_dir/"yearly_commit.png", dpi=300)
plt.close()
