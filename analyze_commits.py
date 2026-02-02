import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

file_path = "requests_commits.csv"

output_dir = Path("analyze_commits_figures")
output_dir.mkdir(exist_ok=True)

commits = []

# 读取数据

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

# 作者提交次数（只记录前十名）

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

# 提交类型分布

merge = dependency = bugfix = feature = 0
refactor = docs = test = release = maintenance = other = 0

for c in commits:
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
    elif any(k in msg for k in [           # 将日常维护等计入此类
    "update", "improve", "change", "adjust", "remove",
    "minor", "tweak", "simplify", "optimize", "handle", "use"
    ]):
        maintenance += 1
    else:
        other += 1

types = [
    "Merge PR",
    "Dependency",
    "Release",
    "Bug Fix",
    "Feature",
    "Refactor",
    "Docs",
    "Test",
    "Maintenance",
    "Other"
]

type_counts = [
    merge,
    dependency,
    release,
    bugfix,
    feature,
    refactor,
    docs,
    test,
    maintenance,
    other
]

plt.figure()
bars = plt.bar(types, type_counts)
plt.xlabel("Commit Type")
plt.ylabel("Number of Commits")
plt.title("Fine-grained Commit Type Distribution")
plt.xticks(rotation=30, ha="right")
for bar, count in zip(bars, type_counts):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5,
             str(count), ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.savefig(output_dir/"commit_type.png", dpi=300)
plt.close()



# 按月份提交统计

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
plt.title("Yearly Commit Activity")
for i, (x, y) in enumerate(zip(years, year_counts)):
    plt.text(x, y + 10.5, str(y), ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(output_dir/"yearly_commit.png", dpi=300)
plt.close()
