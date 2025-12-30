import json
import os

audit_path = r"c:\Users\Greg\Documents\PythonProjects\StatsRecommender\data\expert_audit.json"

with open(audit_path, "r", encoding="utf-8") as f:
    audit = json.load(f)

new_entries = {
    "12717196.json": {
        "title": "Meta-analysis of valvular heart disease treatments",
        "expert_strengths": [
            "Follows PRISMA guidelines and RevMan 5.4.1 used for quantitative synthesis.",
            "Risk of bias assessed using Cochrane Review Manager criteria by dual reviewers.",
            "Heterogeneity assessed with Chi-square and I2 (fixed vs random effects models).",
            "Publication bias evaluated through funnel plot analysis.",
            "Trial Sequential Analysis (TSA) used to evalute power and monitoring boundaries (80% power, 5% alpha)."
        ],
        "critical_gaps": [
            "Threshold for heterogeneity (P > 0.1) is conventional but some sources recommend I2 > 50% as more robust.",
            "Descriptive analysis used when meta-analysis not possible, but criteria for 'not possible' not detailed."
        ],
        "overall_rigor": 8
    },
    "12713972.json": {
        "title": "PSG parameters in children with ADHD and OSA",
        "expert_strengths": [
            "Polysomnography performed in accredited lab following AASM technical standards.",
            "Explicit clinical definitions for OSA based on AHI thresholds (\u22655 and \u22651).",
            "Assumption verification for all tests, with non-parametric (Wilcoxon-Kruskal-Wallis) fallbacks.",
            "Bonferroni adjustment applied for pairwise comparisons between the 4 cohorts.",
            "SAS v9.4 cited for all analyses."
        ],
        "critical_gaps": [
            "No formal sample size/power calculation reported.",
            "Control group (ADHD-/OSA-) lacked normative reference data and served only as a proxy."
        ],
        "overall_rigor": 8
    },
    "12738678.json": {
        "title": "Circulating miRNAs as biomarkers for MASLD",
        "expert_strengths": [
            "Advanced liver imaging (MRI DIXON, ARFI elastography) as reference standards.",
            "Sophisticated miRNA normalization (geometric mean + spike-in spikes) and relative quantification (2^-\u0394Ct).",
            "Internal validation of regression models using optimism-corrected bootstrap (Tibshirani method).",
            "Multivariate logistic regressions adjusted for extensive confounders (age, sex, PA, markers).",
            "Stata 15.0 cited."
        ],
        "critical_gaps": [
            "Loss of information by categorizing continuous liver stiffness/fat based on the median.",
            "No formal power calculation for biomarker discovery phase."
        ],
        "overall_rigor": 9
    },
    "12618250.json": {
        "title": "AAV2i8 gene therapy for heart failure (Phase 1/2)",
        "expert_strengths": [
            "Rigorous bioanalytical assays (ddPCR, ELISpot, Western blot) for transduction and immunogenicity.",
            "Explicit definition of FAS and Safety analysis sets.",
            "Triplicate testing for antigens in ELISpot.",
            "Follows ICH-GCP and Declaration of Helsinki.",
            "SAS v9.4 cited."
        ],
        "critical_gaps": [
            "Explicitly stated that no formal hypothesis testing or power calculations were performed.",
            "Very small sample size (n=18) limits conclusions beyond feasibility."
        ],
        "overall_rigor": 6
    },
    "12673659.json": {
        "title": "Breast density notification randomized trial",
        "expert_strengths": [
            "Triple-arm RCT with allocation concealment and Oracle-based simple randomization.",
            "Co-design process with consumers and multidisciplinary experts.",
            "A priori power calculation with Bonferroni adjustment for 3 pairwise comparisons (alpha=0.017).",
            "Use of GLM (ordinal/multinomial logistic regression) and testing of proportional odds (Brant-Wald).",
            "Sensitivity analysis using MICE for missing primary outcomes."
        ],
        "critical_gaps": [
            "Complete case analysis used as primary despite sensitivity analysis with imputation.",
            "Multiple primary outcomes (3 measures of psychological outcomes) not adjusted beyond pairwise arm comparisons."
        ],
        "overall_rigor": 9
    },
    "12670246.json": {
        "title": "FIMMAC trial: surgery vs placebo vs exercise for shoulder pain",
        "expert_strengths": [
            "Surgical RCT with sham/placebo control arm.",
            "Clinical significance defined via Minimal Important Difference (MID).",
            "Mixed Model for Repeated Measurements (MMRM) to handle missing data under MAR.",
            "Strict multiplicity protection requiring BOTH primary outcomes to be significant.",
            "Internal validation via sensitivity analyses (per protocol, as treated)."
        ],
        "critical_gaps": [
            "High crossover rate (only 56/79 in ASD group fulfilled per-protocol) weakens the pragmatic comparison.",
            "Simple identity covariance structure in mixed model may not capture longitudinal correlation well."
        ],
        "overall_rigor": 9
    },
    "12723751.json": {
        "title": "PGT-A in severe male factor infertility RCT",
        "expert_strengths": [
            "RCT with ITT as primary analysis population.",
            "Power calculation using Hochberg\u2019s procedure for co-primary endpoints (LBR and cLBR).",
            "Generalised linear mixed models (GLMM) used for central effect adjustment.",
            "Non-parametric (Wilcoxon) tests used for non-normal continuous data.",
            "MICE or worst/best-case imputation for missing data."
        ],
        "critical_gaps": [
            "Normality assessment method not explicitly described beyond the choice of non-parametric test."
        ],
        "overall_rigor": 9
    },
    "12723525.json": {
        "title": "Carboplatin in triple-negative breast cancer RCT",
        "expert_strengths": [
            "Observer-blind RCT following CONSORT 2025 guidelines.",
            "Event-driven primary analysis (144 DFS events) with pre-specified power calculation.",
            "Advanced survival modeling including Schoenfeld residual tests for proportional hazards.",
            "Restricted Mean Survival Analysis (RMST) and piecewise HR when PH assumption failed.",
            "Adjustment for non-linear effects of continuous biomarkers (Ki-67) using splines."
        ],
        "critical_gaps": [
            "No formal Type I error control for multiple secondary endpoints."
        ],
        "overall_rigor": 9
    },
    "12721610.json": {
        "title": "URBANE trial: vibegron for OAB in men with BPH",
        "expert_strengths": [
            "Phase 3 double-blind trial with single-blind placebo run-in period.",
            "MMRM analysis to handle longitudinal data and missingness.",
            "Fixed-sequence testing procedure to control family-wise error rate for secondary endpoints.",
            "Centralized IWRS randomization with block stratification by multiple clinically relevant factors.",
            "High statistical power (90-94%) with clear baseline set (FAS)."
        ],
        "critical_gaps": [
            "Randomization was not stratified by site, though centralized. Responder analysis was uncontrolled."
        ],
        "overall_rigor": 9
    },
    "12713916.json": {
        "title": "Systematic review of remote CBT-I for children",
        "expert_strengths": [
            "Follows PRISMA 2020 and Cochrane Handbook standards.",
            "Dual independent reviewers for screening, data extraction, and risk of bias.",
            "Formal Risk of Bias assessment using ROB 2 tool.",
            "Comprehensive search strategy with explicit keyword set and database inclusion."
        ],
        "critical_gaps": [
            "Lack of quantitative meta-analysis (descriptive synthesis only) despite focus on RCTs."
        ],
        "overall_rigor": 8
    }
}

audit.update(new_entries)

with open(audit_path, "w", encoding="utf-8") as f:
    json.dump(audit, f, indent=2)

print(f"Updated expert_audit.json. Total entries: {len(audit)}")
