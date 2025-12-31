import json
import os
import re

class RuleBasedFeedbackEngine:
    def __init__(self):
        pass

    def _add_item(self, list_obj, message, features, category_key, evidence_fallback=None):
        """Helper to add an item with evidence/context."""
        # Find best evidence
        evidence = evidence_fallback
        if not evidence and category_key:
            examples = features.get(category_key, {}).get("examples", [])
            if examples:
                 # Prefer the context of the first match
                 evidence = f"...{examples[0]['context']}..."
            else:
                 # Fallback to unique matches list
                 matches = features.get(category_key, {}).get("unique_matches", [])
                 if matches:
                     evidence = f"Found terms: {', '.join(matches[:3])}"
        
        item = {
            "message": message,
            "evidence": evidence if evidence else "No direct quote found."
        }
        # Deduplicate by message
        if not any(x["message"] == message for x in list_obj):
             list_obj.append(item)

    def generate_feedback(self, features, title=""):
        """
        Processes extracted features to generate deterministic feedback with evidence.
        """
        gaps = []
        recommendations = []
        strengths = []
        
        # --- Domain Detection ---
        # Use explicit domain indicators first, then fallback to general text search if needed
        domain_indicators = features.get("domain_indicators", {}).get("unique_matches", [])
        
        # Also check for widely used terms in other categories if indicators missed (legacy fallback)
        all_text = " ".join([m for cat in features.values() for m in cat.get("unique_matches", [])]).lower()
        if title:
            all_text += " " + title.lower()
        
        # Clinical indicators (Override basic science if present)
        clinical_keywords = ["clinical trial", "randomized", "randomised", "patient", "participant", "phase 1", "phase 2", "phase 3", "human"]
        is_clinical = any(kw in all_text for kw in clinical_keywords)

        basic_science_keywords = ["crystallography", "transcriptomics", "blot", "staining", "mice", "cell line", "seurat", "imagej", "flowjo", "pymol", "bioconductor", "in vitro", "in vivo", "knockout", "fluorescence", "quantification", "western", "microscopy"]
        
        # Only classify as basic science if NOT clinical
        is_basic_science = not is_clinical and ((len(domain_indicators) > 0) or any(kw in all_text for kw in basic_science_keywords))
        
        if is_clinical:
            trigger = next((kw for kw in clinical_keywords if kw in all_text), "clinical context")
            self._add_item(strengths, "Analysis context identifies clinical research (Clinical trial requirements apply).", features, None, evidence_fallback=f"Detected term: '{trigger}'")
        elif is_basic_science:
             # Find which keyword triggered it for evidence
             if domain_indicators:
                 trigger = domain_indicators[0]
             else:
                 trigger = next((kw for kw in basic_science_keywords if kw in all_text), "basic science context")
             self._add_item(strengths, "Analysis context identifies basic science or bioinformatics (Softened clinical trial requirements).", features, None, evidence_fallback=f"Detected term: '{trigger}'")

        # --- Non-Research / Review Detection ---
        # Check Title mainly
        title_lower = title.lower()
        non_research_keywords = ["review", "meta-analysis", "guideline", "consensus", "policy", "perspective", "commentary", "editorial", "retraction", "retracted", "framework", "overview", "statement", "consort", "expression of concern", "erratum", "correction", "corrigendum"]
        is_non_research = any(kw in title_lower for kw in non_research_keywords)
        
        if is_non_research:
             self._add_item(strengths, "Article appears to be Non-Primary Research (Review/Guideline etc.). Statistical gaps suppressed.", features, None, evidence_fallback=f"Detected term in title.")

        # --- Observational Study Detection ---
        observational_keywords = ["cohort", "retrospective", "case-control", "cross-sectional", "registry", "observational", "survey", "scale", "questionnaire", "qualitative", "interview"]
        is_observational = any(kw in all_text for kw in observational_keywords) and not any(kw in all_text for kw in ["randomized", "randomised", "rct"])
        
        if is_observational and not is_basic_science and not is_non_research:
             self._add_item(strengths, "Study design appears Observational (relaxed Blinding/Randomization checks).", features, None, evidence_fallback=f"Detected observational terms.")


        # --- 1. Multiplicity Correction ---
        has_multi = features.get("multiplicity_correction", {}).get("present", False)
        multi_matches = " ".join(features.get("multiplicity_correction", {}).get("unique_matches", [])).lower()
        is_explicit_no_adj = any(re.search(x, multi_matches) for x in ["no adjustment", "no correction", "nominal", r"no.*hypothesis testing"])
        num_p_values = features.get("p_values", {}).get("count", 0)
        
        if has_multi and not is_non_research:
            if is_explicit_no_adj:
                self._add_item(gaps, "Explicitly stated that no multiplicity correction or formal hypothesis testing was performed.", features, "multiplicity_correction")
                recommendations.append({
                    "item": "Multiplicity", 
                    "issue": "Lack of correction increases Type I error.", 
                    "recommendation": "Use Bonferroni or FDR, or label as exploratory.",
                    "source_text": multi_matches[:100]
                })
            else:
                self._add_item(strengths, "Explicitly addressed multiplicity correction for multiple comparisons.", features, "multiplicity_correction")
        elif num_p_values > 5 and not is_non_research:
             # New Rule: Silent Multiplicity
             self._add_item(gaps, f"Detected high number of P-values ({num_p_values}) without explicit mention of multiplicity correction.", features, "p_values")
             recommendations.append({
                 "item": "Multiplicity",
                 "issue": "Multiple testing without correction inflates false positive rate.",
                 "recommendation": "Apply correction (e.g., Bonferroni, Holm) or specify a priori hypotheses.",
                 "source_text": "High P-value count, no 'correction' terms."
             })
        
        # --- 2. Parametric Assumptions ---
        all_unique = []
        for cat in ["comparative_stats", "regression_and_models", "advanced_modeling"]:
             all_unique.extend(features.get(cat, {}).get("unique_matches", []))
        stats_text = " ".join(all_unique).lower()
        is_parametric = any(x in stats_text for x in ["t-test", "anova", "linear model"])
        
        if is_parametric and not features.get("normality_checks", {}).get("present", False) and not is_non_research:
             self._add_item(gaps, "Parametric tests used without documented normality checks.", features, "comparative_stats") 
             recommendations.append({
                 "item": "Assumptions",
                 "issue": "Parametric tests assume normality.",
                 "recommendation": "Report Shapiro-Wilk/KS test or use non-parametric tests.",
                 "source_text": f"Found parametric tests: {', '.join([x for x in ['t-test', 'anova'] if x in stats_text])}"
             })

        # --- 3. Missing Data ---
        if features.get("missing_data", {}).get("present", False) and not is_non_research:
             missing_txt = " ".join(features.get("missing_data", {}).get("unique_matches", [])).lower()
             if "imputation" in missing_txt and "no imputation" not in missing_txt:
                  self._add_item(strengths, "Addressed missing data using imputation methods.", features, "missing_data")
             else:
                  # Check if advanced modeling (MMRM/GLMM) handles it implicitly
                  adv_text = " ".join(features.get("advanced_modeling", {}).get("unique_matches", [])).lower()
                  # Also check the 'regression_and_models' details just in case
                  reg_text = " ".join(features.get("regression_and_models", {}).get("unique_matches", [])).lower()
                  
                  handles_missing_implicitly = any(x in adv_text or x in reg_text for x in ["mixed", "mmrm", "glmm", "gee", "multilevel", "hierarchical"])
                  
                  if handles_missing_implicitly:
                       self._add_item(strengths, "Used Mixed Models (MMRM/GLMM) which can handle missing data under MAR.", features, "advanced_modeling")
                  else:
                       self._add_item(gaps, "Missing data handled via complete-case analysis (potential bias).", features, "missing_data")

        # --- 4. Power & Sample Size (Gated by Basic Science AND Non-Research) ---
        if not is_basic_science and not is_non_research:
             if not features.get("sample_size", {}).get("present", False):
                  self._add_item(gaps, "Sample size justification lacks explicit power calculation details.", features, "sample_size")
                  recommendations.append({
                      "item": "Sample Size",
                      "issue": "No power calculation found.",
                      "recommendation": "Provide alpha, power, and effect size parameters.",
                      "source_text": "No matches for 'power' or 'sample size calculation'"
                  })

        # --- 5. Blinding & Allocation Concealment (Gated by Basic Science AND Observational AND Non-Research) ---
        if not is_basic_science and not is_observational and not is_non_research:
             if features.get("blinding", {}).get("present", False):
                  self._add_item(strengths, "Blinding of participants/assessors documented.", features, "blinding")
                  # Concealment check - ONLY if blinding is present AND not basic science
                  if not features.get("allocation_concealment", {}).get("present", False):
                       self._add_item(gaps, "Blinding present but allocation concealment details missing.", features, "blinding")
                       recommendations.append({
                           "item": "Allocation Concealment",
                           "issue": "Method of concealment (e.g. opaque envelopes) not described.",
                           "recommendation": "Specify how randomization sequence was concealed.",
                           "source_text": "Blinding found but no 'concealment' terms."
                       })
             else:
                  self._add_item(gaps, "Reporting of blinding or masking procedure is missing.", features, None, evidence_fallback="No matches for 'blinded' or 'masked'")

        # --- 6. Software Versions ---
        if features.get("software", {}).get("present", False) and not is_non_research:
             software_matches = features.get("software", {}).get("unique_matches", [])
             has_version = any(re.search(r"v\.?\d|version", s) for s in software_matches)
             if not has_version:
                  self._add_item(gaps, "Software mentioned without specific versions.", features, "software")
             else:
                  self._add_item(strengths, "Detailed software versions provided.", features, "software")

        # --- 7. Reporting Metrics (Effect Sizes & CIs) ---
        if not is_non_research:
            if features.get("effect_sizes", {}).get("present", False):
                 self._add_item(strengths, "Reported effect sizes (e.g., OR, HR, MD) alongside statistical significance.", features, "effect_sizes")
            else:
                 # Only flag missing effect sizes if P-values ARE present
                 if features.get("p_values", {}).get("present", False):
                      self._add_item(gaps, "P-values reported without effect sizes (e.g. Odds Ratio).", features, "p_values")

        # --- 8. Post Hoc vs Planned Analyses ---
        if features.get("post_hoc", {}).get("present", False) and not is_non_research:
            if has_multi and not is_explicit_no_adj:
                self._add_item(strengths, "Performed pre-planned or correctly adjusted post hoc comparisons.", features, "post_hoc")
            else:
                self._add_item(gaps, "Includes exploratory/post hoc analyses without clear multiplicity correction.", features, "post_hoc")
                ph_evidence = features.get("post_hoc", {}).get("unique_matches", ["Post-hoc terms"])[0] 
                recommendations.append({
                    "item": "Deductive Rigor",
                    "issue": "Post hoc findings are hypothesis-generating.",
                    "recommendation": "Distinguish between pre-specified endpoints and exploratory analyses.",
                    "source_text": f"Found term '{ph_evidence}' without rigorous correction."
                })

        # --- 9. Method Suitability: Paired & Categorical ---
        stats_text_lower = stats_text.lower()
        if features.get("dependency", {}).get("present", False) and not is_non_research:
             has_paired = any(x in stats_text_lower for x in ["paired", "wilcoxon", "repeated", "within-subject"])
             if not has_paired:
                  self._add_item(gaps, "Paired data mentioned but no paired statistical tests found.", features, "dependency")
             else:
                  self._add_item(strengths, "Appropriately used paired tests for dependent data.", features, "dependency")
        
        is_categorical = any(x in " ".join(features.get("data_types", {}).get("unique_matches", [])).lower() for x in ["categorical", "frequencies", "proportions"])
        has_cat_test = any(x in stats_text_lower for x in ["chi-square", "fisher", "logistic", "chi2"])
        if is_categorical and not has_cat_test and not is_non_research:
             self._add_item(gaps, "Categorical data mentioned, but no appropriate categorical tests found.", features, "data_types")

        # --- 10. Longitudinal Analysis ---
        dep_clust_text = " ".join(features.get("dependency", {}).get("unique_matches", []) + features.get("clustering", {}).get("unique_matches", [])).lower()
        if any(x in dep_clust_text for x in ["repeated measures", "longitudinal", "cluster", "nested"]) and not is_non_research:
             adv_text = " ".join(features.get("advanced_modeling", {}).get("unique_matches", [])).lower()
             has_adv = any(x in stats_text_lower or x in adv_text for x in ["mixed-effect", "lmm", "glmm", "gee", "multilevel", "hierarchical"])
             if has_adv:
                  self._add_item(strengths, "Accounted for data dependency using advanced modeling.", features, "advanced_modeling")
             else:
                  self._add_item(gaps, "Longitudinal/clustered data detected without hierarchical modeling.", features, "dependency")
                  dep_match = next((x for x in dep_clust_text.split() if x in ["repeated", "longitudinal", "cluster", "nested"]), "Longitudinal data")
                  recommendations.append({
                      "item": "Statistical Architecture",
                      "issue": "Clustered/repeated data requires hierarchical models.",
                      "recommendation": "Use LMM, GLMM, or GEE.",
                      "source_text": f"Found '{dep_match}' but no mixed-effects models."
                  })

        # --- 11. ANOVA Post-hoc ---
        if "anova" in stats_text_lower and not features.get("post_hoc", {}).get("present", False) and not is_non_research:
             self._add_item(gaps, "ANOVA mentioned without specifying post-hoc tests.", features, "comparative_stats")

        # --- 12. Survival Analysis ---
        if features.get("survival_analysis", {}).get("present", False):
             asm_text = " ".join(features.get("assumption_checks", {}).get("unique_matches", [])).lower()
             if "schoenfeld" in asm_text or "proportional hazards" in asm_text:
                  self._add_item(strengths, "Verified proportional hazards assumption.", features, "assumption_checks")
             else:
                  self._add_item(gaps, "Survival analysis used without verifying proportional hazards assumption.", features, "survival_analysis")

        # --- 13. Baseline P-values in RCT ---
        if features.get("randomization", {}).get("present", False) and features.get("baseline_reporting", {}).get("present", False):
             base_ctx = str(features.get("baseline_reporting", {}).get("examples", [])).lower()
             if "p=" in base_ctx or "p <" in base_ctx:
                  self._add_item(gaps, "Potential use of P-values for baseline comparisons in an RCT.", features, "baseline_reporting")

        # --- 14. Exact P-values ---
        p_ex = features.get("p_values", {}).get("examples", [])
        has_exact = any("=" in m["match"] for m in p_ex)
        if features.get("p_values", {}).get("present", False) and not has_exact and not is_basic_science and not is_non_research:
             self._add_item(gaps, "P-values reported only as thresholds (e.g., P<0.05).", features, "p_values")

        # --- 15. Bias, Exclusion & Model Details ---
        adv_extra_text = " ".join(features.get("advanced_modeling_extra", {}).get("unique_matches", [])).lower()
        if "exclud" in adv_extra_text or "exclusion" in adv_extra_text:
             # Refined: Exclusion criteria is GOOD if explicit. Only flag if language suggests bias (hard to do with regex, so just mark strength for now)
             self._add_item(strengths, "Exclusion criteria explicitly defined (transparency).", features, "advanced_modeling_extra")
        if "compliance" in adv_extra_text or "attrition" in adv_extra_text:
             self._add_item(strengths, "Documented participant compliance or attrition.", features, "advanced_modeling_extra")
        
        # --- 16. Meta-Analysis (Refined) ---
        sr_matches = features.get("systematic_review_metrics", {}).get("unique_matches", [])
        sr_text = " ".join(sr_matches).lower()
        is_strong_ma = (features.get("systematic_review_metrics", {}).get("count", 0) > 1) or \
                       any(x in sr_text for x in ["sucra", "i2", "heterogeneity", "credible interval", "dic"])
        
        if features.get("systematic_review_metrics", {}).get("present", False) and is_strong_ma:
             self._add_item(strengths, "Detailed reporting of network/meta-analysis metrics.", features, "systematic_review_metrics")
             if "credible interval" in sr_text:
                  self._add_item(strengths, "Used Bayesian framework for evidence synthesis.", features, "systematic_review_metrics")
             if ("i2" in sr_text or "heterogeneity" in sr_text) and "threshold" not in sr_text and not is_basic_science:
                  self._add_item(gaps, "Heterogeneity (I2) mentioned without significance threshold.", features, "systematic_review_metrics")
             if any(x in sr_text for x in ["fragmented", "fragmentation"]):
                  self._add_item(gaps, "Network fragmentation detected in systematic review.", features, "systematic_review_metrics")

        # --- 17. Diagnostic Metrics ---
        if features.get("diagnostic_metrics", {}).get("present", False):
             self._add_item(strengths, "Reported diagnostic metrics (AUC/ROC).", features, "diagnostic_metrics")
             diag_text = " ".join(features.get("diagnostic_metrics", {}).get("unique_matches", [])).lower()
             if ("auc" in diag_text or "roc" in diag_text) and not features.get("confidence_intervals", {}).get("present", False):
                  self._add_item(gaps, "Diagnostic metrics reported without Confidence Intervals.", features, "diagnostic_metrics")

        # --- Scoring ---
        # Calculate score properties
        # Basic heuristic: Start at 10, deduct for gaps.
        # Basic Science floor is higher (6.0) if no major stats errors found.
        deductions = len(gaps) * 1.5
        score = max(1.0, 10.0 - deductions)
        
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
