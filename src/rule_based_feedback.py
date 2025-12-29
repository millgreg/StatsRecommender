import json
import os
import re

class RuleBasedFeedbackEngine:
    def __init__(self):
        pass

    def generate_feedback(self, features):
        """
        Processes extracted features to generate deterministic feedback.
        """
        gaps = []
        recommendations = []
        strengths = []
        
        if features.get("multiplicity_correction", {}).get("present", False):
            strengths.append("Explicitly addressed multiplicity correction for multiple comparisons.")
        elif features.get("comparative_stats", {}).get("count", 0) > 2 or features.get("interaction_subgroup", {}).get("present", False):
            gaps.append("Missing multiplicity correction despite multiple comparative tests or subgroup analyses.")
            recommendations.append({
                "item": "Multiplicity",
                "issue": "Multiple statistical comparisons or subgroups analyzed without documented alpha adjustment.",
                "recommendation": "Apply Bonferroni, Benjamini-Hochberg, or similar correction for multiple testing."
            })

        # 2. Parametric Assumption Rules
        # Combine all statistical keywords and contexts for searching
        stats_examples = (
            features.get("comparative_stats", {}).get("examples", []) +
            features.get("regression_and_models", {}).get("examples", []) +
            features.get("advanced_modeling", {}).get("examples", []) +
            features.get("clustering", {}).get("examples", []) +
            features.get("dependency", {}).get("examples", [])
        )
        stats_text = str(stats_examples).lower()
        is_parametric = any(x in stats_text for x in ["t-test", "anova", "linear model"])
        
        if is_parametric:
            if not features.get("normality_checks", {}).get("present", False):
                gaps.append("Parametric tests used without documented normality checks.")
                recommendations.append({
                    "item": "Assumptions",
                    "issue": "Parametric tests (t-test/ANOVA) used without verifying the assumption of normality.",
                    "recommendation": "Report Shapiro-Wilk or Kolmogorov-Smirnov test results, or use non-parametric alternatives if data is skewed."
                })
        
        if features.get("normality_checks", {}).get("present", False):
            strengths.append("Normality of data distribution was explicitly checked.")

        # 3. Method Suitability: Paired vs Unpaired
        is_paired_data = features.get("dependency", {}).get("present", False)
        paired_tests = ["paired t-test", "wilcoxon matched", "signed-rank", "repeated measures"]
        stats_text_lower = stats_text.lower()
        has_paired_test = any(x in stats_text_lower for x in paired_tests)
        
        if is_paired_data and not has_paired_test:
            gaps.append("Dataset mentioned as 'paired' or 'matched', but no paired statistical tests found.")
            recommendations.append({
                "item": "Method Suitability",
                "issue": "Use of unpaired tests on dependent/paired data reduces statistical power and can be incorrect.",
                "recommendation": "Use paired t-test, Wilcoxon signed-rank test, or repeated measures ANOVA for dependent samples."
            })
        elif is_paired_data and has_paired_test:
            strengths.append("Appropriately used paired tests for dependent data structures.")

        # 4. Method Suitability: Categorical vs Continuous
        is_categorical = any(x in str(features.get("data_types", {}).get("examples", [])).lower() for x in ["categorical", "frequencies", "binary"])
        has_categorical_test = any(x in stats_text_lower for x in ["chi-square", "fisher", "logistic regression"])
        
        if is_categorical and not has_categorical_test:
            gaps.append("Categorical data mentioned, but no appropriate categorical tests (e.g., Chi-square) found.")
            recommendations.append({
                "item": "Method Suitability",
                "issue": "Missing categorical comparative analysis for frequency-based data.",
                "recommendation": "Report Chi-square or Fisher's exact test results for categorical outcome variables."
            })

        # 5. Longitudinal & Clustered Data (Unit of Analysis)
        has_dependency = features.get("dependency", {}).get("present", False) or features.get("clustering", {}).get("present", False)
        longitudinal_keywords = ["repeated measures", "longitudinal", "cluster", "nested", "multilevel"]
        is_specifically_longitudinal = any(x in str(features.get("dependency", {}).get("examples", []) + features.get("clustering", {}).get("examples", [])).lower() for x in longitudinal_keywords)
        
        advanced_modeling_text = str(features.get("advanced_modeling", {}).get("examples", [])).lower()
        has_advanced_model = any(x in stats_text_lower or x in advanced_modeling_text for x in ["mixed-effect", "lmm", "glmm", "gee", "repeated measures anova", "multilevel", "hierarchical", "random intercept", "random effect", "nested"])
        
        if is_specifically_longitudinal and not has_advanced_model:
            gaps.append("Longitudinal or clustered data mentioned, but no hierarchical/mixed-effects modeling found.")
            recommendations.append({
                "item": "Statistical Architecture",
                "issue": "Unit of Analysis Error: Nested or repeated data points are not independent and require special handling.",
                "recommendation": "Use Linear Mixed Models (LMM), GEE, or Repeated Measures ANOVA to account for within-subject correlations."
            })
        elif is_specifically_longitudinal and has_advanced_model:
            strengths.append("Correctly accounted for data dependency using advanced longitudinal modeling.")

        # 6. ANOVA Post-hoc Quality
        if "anova" in stats_text_lower and not features.get("post_hoc", {}).get("present", False):
            gaps.append("ANOVA mentioned without specifying post-hoc tests for group comparisons.")
            recommendations.append({
                "item": "Reporting Rigor",
                "issue": "ANOVA only identifies overall significance; post-hoc tests are needed to find specific group differences.",
                "recommendation": "Specify and report post-hoc tests (e.g., Tukey, Bonferroni) following a significant ANOVA."
            })

        # 7. Reporting Quality: Effect Sizes (Nature Standard)
        if features.get("p_values", {}).get("present", False) and not features.get("effect_size", {}).get("present", False):
            gaps.append("P-values reported without corresponding effect sizes or measures of magnitude.")
            recommendations.append({
                "item": "Reporting Rigor",
                "issue": "High-impact journals require reporting effect sizes (e.g., mean differences, odds ratios) alongside p-values.",
                "recommendation": "Include effect sizes (e.g., Cohen's d, Relative Risk, or absolute differences) with 95% Confidence Intervals."
            })
        elif features.get("effect_size", {}).get("present", False):
            strengths.append("Reported effect sizes alongside statistical significance.")

        # 6. Survival Analysis Assumptions
        if features.get("survival_analysis", {}).get("present", False):
            if not features.get("assumption_checks", {}).get("present", False):
                gaps.append("Survival analysis (Cox/Log-rank) used without verifying Proportional Hazards assumption.")
                recommendations.append({
                    "item": "Assumptions (Survival)",
                    "issue": "Proportional hazards assumption for Cox regression not documented.",
                    "recommendation": "Report Schoenfeld residual tests or log-log plots to verify the proportional hazards assumption."
                })
        
        if features.get("assumption_checks", {}).get("present", False):
            strengths.append("Statistical model assumptions (e.g., PH assumption) were explicitly verified.")

        # 4. Design Transparency
        sample_size_matches = str(features.get("sample_size", {}).get("examples", [])).lower()
        if any(x in sample_size_matches for x in ["power", "calculation"]):
            if "approximate" in sample_size_matches:
                gaps.append("Sample size calculation uses 'approximate' rates which could be more precise.")
                recommendations.append({
                    "item": "Sample Size",
                    "issue": "Power analysis mentions 'approximate' values rather than precise estimates.",
                    "recommendation": "Provide exact assumptions and point estimates used in the power calculation."
                })
            strengths.append("Sample size was justified with a formal power calculation.")
        else:
            gaps.append("Sample size justification lacks explicit power calculation details.")
            recommendations.append({
                "item": "Sample Size",
                "issue": "Power analysis not explicitly described.",
                "recommendation": "Provide details on alpha, power, and expected effect size used to determine sample size."
            })

        if features.get("blinding", {}).get("present", False):
            strengths.append("Blinding of participants or assessors was documented.")
            if not features.get("allocation_concealment", {}).get("present", False):
                gaps.append("Blinding description lacks detail on the allocation concealment process.")
                recommendations.append({
                    "item": "Trial Reporting",
                    "issue": "Blinding is mentioned, but the method of concealing assignments (e.g., opaque envelopes) is not specified.",
                    "recommendation": "Clearly describe the mechanism used to implement the random allocation sequence (e.g., sequentially numbered containers)."
                })
        else:
            gaps.append("Reporting of blinding procedure is missing.")
        
        if features.get("allocation_concealment", {}).get("present", False):
            strengths.append("Documented the allocation concealment process.")

        # 4b. Analysis Principles (ITT)
        if features.get("itt_details", {}).get("present", False) or features.get("analysis_principles", {}).get("present", False):
            strengths.append("Used an Intention-to-Treat (ITT) approach for analysis.")
            
        # 4c. Interaction and Subgroup Analysis
        if features.get("interaction_subgroup", {}).get("present", False):
            strengths.append("Performed explicit interaction and subgroup analyses.")

        # 10. Baseline Comparison P-values
        if features.get("randomization", {}).get("present", False) and features.get("baseline_reporting", {}).get("present", False):
            # Check if p-values are mentioned in the context of baseline
            baseline_context = str(features.get("baseline_reporting", {}).get("examples", [])).lower()
            if "p=" in baseline_context or "p <" in baseline_context:
                gaps.append("Potential use of P-values for baseline comparisons in an RCT.")
                recommendations.append({
                    "item": "Trial Reporting",
                    "issue": "CONSORT discourages P-values for baseline characteristics as any differences are due to chance.",
                    "recommendation": "Assess baseline balance by clinical relevance/magnitude of difference rather than statistical significance."
                })

        # 8. Exact P-values Check
        p_matches = [m["match"] for m in features.get("p_values", {}).get("examples", [])]
        has_exact_p = any("=" in m for m in p_matches)
        if features.get("p_values", {}).get("present", False) and not has_exact_p:
            gaps.append("P-values reported only as thresholds (e.g., P<0.05).")
            recommendations.append({
                "item": "Reporting Quality",
                "issue": "Precise P-values are preferred over threshold-based reporting.",
                "recommendation": "Report exact P-values (e.g., P=0.034) for all primary analyses."
            })

        # 9. Software Version Reporting
        software_matches = [m["match"] for m in features.get("software", {}).get("examples", [])]
        has_version = any(re.search(r"version|\d+", m.lower()) for m in software_matches)
        if features.get("software", {}).get("present", False) and not has_version:
            gaps.append("Software mentioned without specific version numbers.")
            recommendations.append({
                "item": "Reproducibility",
                "issue": "Specific software versions are required for statistical reproducibility.",
                "recommendation": "Cite the exact version number (e.g., Stata v18, R 4.3.1) and any specific packages used."
            })
        elif features.get("software", {}).get("present", False) and has_version:
            strengths.append("Provided specific software version details for reproducibility.")

        # Overall Rigor Score (Simple heuristic)
        max_score = 10
        deductions = len(gaps) * 1.5
        score = max(1, min(10, max_score - deductions))

        return {
            "overall_score": round(score, 1),
            "rigor_rating": "High" if score >= 8 else "Medium" if score >= 5 else "Low",
            "critical_gaps": gaps,
            "strengths": strengths,
            "actionable_recommendations": recommendations,
            "deterministic_audit": True
        }

def process_all_features(features_folder="data/features", output_folder="data/feedback"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    engine = RuleBasedFeedbackEngine()
    
    for filename in os.listdir(features_folder):
        if filename.endswith(".json"):
            with open(os.path.join(features_folder, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            
            features = data.get("features", {})
            print(f"Generating rule-based feedback for: {filename}")
            feedback = engine.generate_feedback(features)
            
            output_data = {
                "title": data.get("title"),
                "pmcid": data.get("pmcid"),
                "features": features,
                "feedback": feedback
            }
            
            output_path = os.path.join(output_folder, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved feedback to: {output_path}")

if __name__ == "__main__":
    process_all_features()
