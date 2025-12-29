import os
import json

features_dir = "data/features"
results = []

if not os.path.exists(features_dir):
    print(f"Directory {features_dir} not found.")
    exit(1)

for filename in os.listdir(features_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(features_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            features = data.get("features", {})
            results.append({
                "file": filename,
                "multiplicity": features.get("multiplicity_correction", {}).get("present", False),
                "normality": features.get("normality_checks", {}).get("present", False)
            })

results.sort(key=lambda x: x['file'])

if not results:
    print("No features extracted yet.")
    exit(0)

print(f"{'File':<25} | {'Multiplicity':<15} | {'Normality':<10}")
print("-" * 60)
for r in results:
    print(f"{r['file']:<25} | {str(r['multiplicity']):<15} | {str(r['normality']):<10}")

print(f"\nTotal files summarized: {len(results)}")
