import os
import json
import glob
import matplotlib
matplotlib.use('Agg') # Force non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter

def generate_visuals():
    print("Step 1: finding files...")
    
    # 1. Load Data
    data = []
    files = glob.glob("data/feedback/*.json")
    print(f"Found {len(files)} feedback files.")
    
    if len(files) == 0:
        print("WARNING: No feedback files found!")
        return

    print("Step 2: Processing data...")
    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            content = json.load(file)
            fb = content.get("feedback", {})
            gaps = [g["message"] for g in fb.get("critical_gaps", [])]
            strengths = [s["message"] for s in fb.get("strengths", [])]
            
            # Infer Type
            study_type = "Clinical Trial" # Default
            if any("Observational" in s for s in strengths):
                study_type = "Observational"
            elif any("Basic Science" in s for s in strengths):
                study_type = "Basic Science"
            elif any("Non-Primary Research" in s for s in strengths):
                study_type = "Review/Meta"
            
            data.append({
                "Filename": os.path.basename(f),
                "Score": fb.get("overall_score", 0),
                "Type": study_type,
                "Gaps": gaps
            })
            
    df = pd.DataFrame(data)
    print(f"Dataframe created with {len(df)} rows.")
    
    # Create output dir
    out_dir = "reports/figures"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    print("Step 3: Generating Figure 1 (Score Distribution)...")
    try:
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        sns.histplot(data=df, x="Score", kde=True, bins=10, hue="Type", multiple="stack")
        plt.title("Distribution of Statistical Rigor Scores (N={})".format(len(df)))
        plt.xlabel("Rigor Score (0-10)")
        plt.ylabel("Number of Papers")
        plt.savefig(os.path.join(out_dir, "fig1_score_distribution.png"), dpi=300)
        plt.close()
        print("Figure 1 saved.")
    except Exception as e:
        print(f"Error generating Figure 1: {e}")
    
    print("Step 4: Generating Figure 2 (Heatmap)...")
    try:
        # Unroll gaps
        gap_data = []
        for _, row in df.iterrows():
            for gap in row["Gaps"]:
                 gap_data.append({"Type": row["Type"], "Gap": gap})
                 
        gap_df = pd.DataFrame(gap_data)
        
        if not gap_df.empty:
            plt.figure(figsize=(12, 8))
            # Get top 10 gaps total
            top_gaps = gap_df["Gap"].value_counts().head(10).index
            gap_df_top = gap_df[gap_df["Gap"].isin(top_gaps)]
            
            # Calculate percentages per Type
            counts = gap_df_top.groupby(["Type", "Gap"]).size().reset_index(name="Count")
            totals = df["Type"].value_counts().reset_index()
            totals.columns = ["Type", "Total"]
            
            merged = pd.merge(counts, totals, on="Type")
            merged["Prevalence"] = (merged["Count"] / merged["Total"]) * 100
            
            pivot = merged.pivot(index="Gap", columns="Type", values="Prevalence").fillna(0)
            
            sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Prevalence (%)'})
            plt.title("Prevalence of Statistical Gaps by Study Type")
            plt.tight_layout()
            plt.savefig(os.path.join(out_dir, "fig2_gap_heatmap.png"), dpi=300)
            plt.close()
            print("Figure 2 saved.")
        else:
            print("Skipping Figure 2 (No Gaps Found)")
    except Exception as e:
        print(f"Error generating Figure 2: {e}")

    print(f"Figures saved to {os.path.abspath(out_dir)}")

if __name__ == "__main__":
    try:
        generate_visuals()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
