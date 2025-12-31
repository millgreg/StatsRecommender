import json
import os
import glob
from collections import Counter

def generate_dashboard(feedback_dir="data/feedback", output_path="reports/rigor_dashboard.html"):
    if not os.path.exists("reports"):
        os.makedirs("reports")

    feedback_files = glob.glob(os.path.join(feedback_dir, "*.json"))
    all_data = []
    all_gaps = []
    all_strengths = []
    basic_science_count = 0
    
    for fpath in feedback_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Basic info
            entry = {
                "filename": os.path.basename(fpath),
                "title": data.get("title", "Unknown Title"),
                "score": data.get("feedback", {}).get("overall_score", 0),
                "rating": data.get("feedback", {}).get("rigor_rating", "Unknown"),
                "gaps": data.get("feedback", {}).get("critical_gaps", []),
                "strengths": data.get("feedback", {}).get("strengths", [])
            }
            all_data.append(entry)
            all_gaps.extend([g["message"] for g in entry["gaps"]]) # Extract message string
            all_strengths.extend([s["message"] for s in entry["strengths"]])
            
            # Check for basic science domain
            if any("Basic Science" in s["message"] for s in entry["strengths"]):
                 basic_science_count += 1

    # Aggregate common problems
    # Aggregate common problems & strengths
    gap_counts = Counter(all_gaps)
    common_problems = gap_counts.most_common(6)
    
    strength_counts = Counter(all_strengths)
    common_strengths = strength_counts.most_common(6)

    # Sort data by score (descending)
    all_data.sort(key=lambda x: x["score"], reverse=True)

    # Calculate global stats
    avg_score = sum(e["score"] for e in all_data) / len(all_data) if all_data else 0
    high_rigor_pct = len([e for e in all_data if e["score"] >= 7]) / len(all_data) * 100 if all_data else 0

    # CSS Content (inline for portability)
    css_path = os.path.join(os.path.dirname(__file__), "dashboard.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        css_content = "/* CSS missing */"

    # HTML Template
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Statistical Rigor Dashboard</title>
    <style>{css_content}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Statistical Rigor Dashboard</h1>
            <p>Automated auditing of {len(all_data)} scientific papers across clinical and computational domains.</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-value">{len(all_data)}</span>
                <span class="stat-label">Papers Audited</span>
            </div>
            <div class="stat-card" style="border-color: var(--accent-success)">
                <span class="stat-value" style="color: var(--accent-success)">{avg_score:.1f}/10</span>
                <span class="stat-label">Average Rigor Score</span>
            </div>
            <div class="stat-card" style="border-color: var(--accent-primary)">
                <span class="stat-value">{high_rigor_pct:.0f}%</span>
                <span class="stat-label">High Rigor Rate</span>
            </div>
            <div class="stat-card" style="border-color: #818cf8">
                <span class="stat-value" style="color: #818cf8">{basic_science_count}</span>
                <span class="stat-label">Basic Science Papers</span>
            </div>
        </div>

        <section class="problem-section">
            <h2>⚠️ Recurring Problematic Points</h2>
            <div class="problem-list">
                {"".join(f'<div class="problem-item"><b>{gap}</b> Found in {count} papers</div>' for gap, count in common_problems)}
            </div>
        </section>

        <section class="strength-section">
            <h2>✅ Common Strengths</h2>
            <div class="strength-list">
                {"".join(f'<div class="strength-item"><b>{strength}</b> Found in {count} papers</div>' for strength, count in common_strengths)}
            </div>
        </section>

        <section class="card">
            <table>
                <thead>
                    <tr>
                        <th>Paper Title</th>
                        <th>Score</th>
                        <th>Critical Gaps</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f'''
                    <tr>
                        <td>
                            <div class="truncate" title="{e['title']}">{e['title']}</div>
                            <small style="color: var(--text-muted)">{e['filename']}</small>
                        </td>
                        <td>
                            <div class="score-container">
                                <span class="score-pill score-{e['rating'].lower()}">{e['score']:.1f}</span>
                                <div class="score-bar-bg">
                                    <div class="score-bar-fill" style="width: {e['score'] * 10}%"></div>
                                </div>
                            </div>
                        </td>
                        <td>
                            <ul class="gaps-list">
                                {"".join(f"<li>{g}</li>" for g in e['gaps'][:2])}
                                {f"<li>...and {len(e['gaps'])-2} more</li>" if len(e['gaps']) > 2 else ""}
                            </ul>
                        </td>
                    </tr>
                    ''' for e in all_data)}
                </tbody>
            </table>
        </section>

        <footer>
            Generated by StatsRecommender Auditor &bull; 2025
        </footer>
    </div>
</body>
</html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"Dashboard successfully generated at: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    generate_dashboard()
