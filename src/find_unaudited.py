import json
import os

audit_path = r"c:\Users\Greg\Documents\PythonProjects\StatsRecommender\data\expert_audit.json"
processed_dir = r"c:\Users\Greg\Documents\PythonProjects\StatsRecommender\data\processed"

with open(audit_path, "r", encoding="utf-8") as f:
    audited = json.load(f).keys()

all_processed = [f for f in os.listdir(processed_dir) if f.endswith(".json")]
unaudited = [f for f in all_processed if f not in audited]

print(f"Total processed: {len(all_processed)}")
print(f"Already audited: {len(audited)}")
print(f"Unaudited: {len(unaudited)}")
print("First 10 unaudited:")
for f in unaudited[:10]:
    print(f)
