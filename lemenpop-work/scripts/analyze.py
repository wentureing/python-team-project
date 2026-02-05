import pandas as pd

print("=== Commit Analysis Tool===")
print("Author：lemenpop")

# 简单数据
data = [
    ["Fix bug", "2026-02-05"],
    ["Add feature", "2026-02-05"],
    ["Update documentation", "2026-02-05"]
]

for item in data:
    print(f"- {item[0]} ({item[1]})")

print("\\nAnalysis completed")