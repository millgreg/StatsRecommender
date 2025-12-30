import json
import os

audit_path = r"c:\Users\Greg\Documents\PythonProjects\StatsRecommender\data\expert_audit.json"

with open(audit_path, "r", encoding="utf-8") as f:
    audit = json.load(f)

new_entries = {
    # Batch 3
    "12721662.json": {
        "title": "STRATA trial: Cxbladder Triage for microhematuria",
        "expert_strengths": [
            "Multicenter prospective study with 12 sites and randomization (2:1).",
            "Explicit power calculation to detect reduction in cystoscopy rates.",
            "Use of prop.test in R for proportions and exact binomial CIs for validity metrics (NPV, sensitivity).",
            "Follow-up period (3-24 months) used to confirm absence of disease in non-surgical patients.",
            "Analysis done in R 4.2.10."
        ],
        "critical_gaps": [
            "Discrepancies in patient totals between validity and utility populations due to strict review criteria.",
            "Potential for misclassification if the follow-up period was too short for occult UC."
        ],
        "overall_rigor": 8
    },
    "12721647.json": {
        "title": "Psychological comorbidities in women with Fowler's syndrome",
        "expert_strengths": [
            "Standardized multidisciplinary assessment including ICS-standard invasive urodynamics.",
            "Advanced neuro-urological tests (Brown-Wickham UPP and concentric needle EMG).",
            "Semi-structured psychological interviews by a chartered psychologist using validated screens (GAD-2, PHQ-2).",
            "Data-driven choice of tests (mean/SD vs median/range) and comparative stats (\u03c72, Fisher's, t-test)."
        ],
        "critical_gaps": [
            "Clinical audit/service evaluation design rather than formal prospective protocol.",
            "Small sample sizes for specific invasive tests (n=62-79)."
        ],
        "overall_rigor": 7
    },
    "12705465.json": {
        "title": "RELATIVITY-098: Adjuvant nivolumab and relatlimab in melanoma",
        "expert_strengths": [
            "Large phase 3 RCT (n=1050) with O'Brien-Fleming alpha spending function for interim analyses.",
            "Hierarchical testing of secondary endpoints to control Type I error.",
            "Sophisticated biomarker imaging/analysis using CODEX PhenoCycler and HALO AI.",
            "Longitudinal modeling (linear mixed-effects) and non-parametric Wilcoxon tests for biomarkers.",
            "SAS and R v4.3.1 cited."
        ],
        "critical_gaps": [
            "Biomarker analyses labeled as exploratory, reducing rigor for those secondary findings."
        ],
        "overall_rigor": 9
    },
    "12705419.json": {
        "title": "EDGE-Gastric trial: domvanalimab and zimberelimab in GC/GEJC/EAC",
        "expert_strengths": [
            "Multicenter study with central PD-L1 assessment (VENTANA SP263 assay).",
            "Exact binomial Clopper-Pearson 90% CIs for ORR and log-log transformation for survival CIs.",
            "Precise AE monitoring using MedDRA v25.0 and NCI-CTCAE v5.0.",
            "SAS v9.4 cited."
        ],
        "critical_gaps": [
            "Descriptive design explicitly avoiding formal hypothesis testing or power considerations.",
            "Open-label (unblinded) and small sample size (n=41) in the reported arm."
        ],
        "overall_rigor": 7
    },
    "12714473.json": {
        "title": "Induction vs. Adjuvant Chemotherapy in NPC: A propensity-matched study",
        "expert_strengths": [
            "Use of Propensity Score Matching (PSM) with a stringent caliper (0.01) to control for selection bias.",
            "Standardized oncology endpoints (OS, FFS, LRRFS, DMFS) following RECIST.",
            "Standardized radiotherapy (IMRT) following ICRU guidelines.",
            "Cox proportional hazards model with 95% CIs and Kaplan-Meier analysis.",
            "SPSS v23.0 cited."
        ],
        "critical_gaps": [
            "Retrospective nature limits causal inference despite PSM.",
            "Categorization of continuous variables may lead to information loss."
        ],
        "overall_rigor": 8
    },
    "12713946.json": {
        "title": "Sleep Monitoring App in Military Primary Care",
        "expert_strengths": [
            "Mixed-methods pilot study evaluating both quantitative app data and qualitative PCM feedback.",
            "Approved by WRNMMC IRB.",
            "Educational components tailored to military population."
        ],
        "critical_gaps": [
            "Lack of detailed statistical methodology for quantitative outcomes in the Methods section.",
            "Non-randomized, feasibility-focused design."
        ],
        "overall_rigor": 5
    },
    # Batch 4
    "7618412.json": {
        "title": "Availability and order on sustainable food choices",
        "expert_strengths": [
            "Factorial RCT (Availability x Order) with explicit power calculation (n=1053).",
            "Robust data handling: switched to eco-quintile analysis when primary data was found to be bimodal.",
            "Welch ANOVA and Games-Howell used for unequal variances.",
            "Strict multiplicity control (p < 0.003) for secondary/exploratory outcomes.",
            "R v4.1.3 and specific packages (dplyr, ggplot2, rstatix) cited."
        ],
        "critical_gaps": [
            "Deviated from pre-specified plan for ecoscore to handle bimodal distribution."
        ],
        "overall_rigor": 9
    },
    "12647978.json": {
        "title": "Impact of an SMS intervention on nutrition in Nepal",
        "expert_strengths": [
            "Large-scale cluster-randomized trial (134 clusters) with Difference-in-Differences (DiD) ITT analysis.",
            "Cluster-level adjustments using a sandwich estimator.",
            "Concealed allocation to PIs and data collectors.",
            "Data collection using ODK with logic checks and equity tools for wealth quintiles.",
            "Stata/SE 14.2 cited."
        ],
        "critical_gaps": [
            "Significant data missingness and delays due to COVID-19 pandemic.",
            "Exposure to similar health messages in control areas (contamination)."
        ],
        "overall_rigor": 8
    },
    "12705423.json": {
        "title": "DESTINY-Breast04: T-DXd in HER2-low metastatic breast cancer",
        "expert_strengths": [
            "Phase 3 RCT (2:1) with central HER2 confirmation and blinded independent central review (BICR).",
            "Hierarchical testing procedure for OS to preserve alpha.",
            "Assumption checks: visual inspection of log-log survival functions.",
            "Independent adjudication for sensitive AEs (ILD/pneumonitis).",
            "SAS v9.3 cited."
        ],
        "critical_gaps": [
            "Open-label design. No imputation for missing data (censoring only)."
        ],
        "overall_rigor": 9
    },
    "12728524.json": {
        "title": "In silico drug target identification for NAFLD",
        "expert_strengths": [
            "Comprehensive computational pipeline (Homology modeling, docking, MD simulations, pharmacophore).",
            "Use of verified servers (SAVES v5.0) and software (AutoDock Vina, Desmond, LIGPLOT).",
            "Drug-likeness filters based on multiple established rules (Lipinski, Veber, Ghose).",
            "Free energy calculations via MM-GBSA and stability checking with PCA in R."
        ],
        "critical_gaps": [
            "Lack of experimental (in vitro/in vivo) validation for predicted leads.",
            "Strict p-value (0.01) for GEO dataset but no FDR correction mentioned."
        ],
        "overall_rigor": 8
    },
    "12727047.json": {
        "title": "Surgical RCT for post-operative management in India",
        "expert_strengths": [
            "Prospectively registered RCT (CTRI/2019/08/020879).",
            "Use of distribution-appropriate tests (t-test/Mann-Whitney) and categorical checks (\u03c72/Fisher's)."
        ],
        "critical_gaps": [
            "Brief methodology lacking power or sample size justification in the reported snippet."
        ],
        "overall_rigor": 6
    },
    # Batch 5
    "12714465.json": {
        "title": "CCND1 copy number alterations in oral cancer",
        "expert_strengths": [
            "Prospective observational study with molecular validation (Qf-PCR) and IHC correlation.",
            "Explicit cutoff (1.8 fold change) using \u0394\u0394Ct method for genetic amplification.",
            "Quantitative IHC scoring system (integrated intensity and percentage).",
            "SPSS used for \u03c72, ANOVA, and logistic regression."
        ],
        "critical_gaps": [
            "Small sample size (n=63) and single-center design."
        ],
        "overall_rigor": 8
    },
    "12714475.json": {
        "title": "Diagnostic ability of DOI for lymph node metastasis in oral cancer",
        "expert_strengths": [
            "Prospective observational study with standardized pathology (CAP protocol).",
            "Advanced multivariate modeling: multiple binary logistic regression and nomogram construction.",
            "Diagnostic validation: ROC, AUC, sensitivity, specificity, PPV, NPV, and Hosmer-Lemeshow fit.",
            "SPSS v26, STATA v14, and R v4.0.3 cited."
        ],
        "critical_gaps": [
            "Single-center tertiary care setting may limit external generalizability."
        ],
        "overall_rigor": 9
    },
    "12727006.json": {
        "title": "Clinicopathological profile of EOC in India",
        "expert_strengths": [
            "Detailed surgical assessment (PCI, SCS, CC score) and complications (Clavien-Dindo).",
            "Appropriate non-parametric (Kruskal-Wallis, Mann-Whitney) and categorical (Fisher's exact) tests.",
            "SPSS v21.0 cited."
        ],
        "critical_gaps": [
            "Purely observational/descriptive cohort; no power calculations reported."
        ],
        "overall_rigor": 7
    },
    "12727007.json": {
        "title": "Cancer incidence and trends in Bam City, Iran",
        "expert_strengths": [
            "Population-based registry data integrated with clinical/histological sources.",
            "ICD-O coding and Age-Standardized Rates (ASRs) computed using World Standard Population.",
            "Demographic context provided (population pyramids).",
            "SPSS v22 and GraphPad Prism 9 cited."
        ],
        "critical_gaps": [
            "Simple cross-sectional analysis without advanced trend modeling (joinpoint)."
        ],
        "overall_rigor": 6
    }
}

audit.update(new_entries)

with open(audit_path, "w", encoding="utf-8") as f:
    json.dump(audit, f, indent=2)

print(f"Updated expert_audit.json. Total entries: {len(audit)}")
