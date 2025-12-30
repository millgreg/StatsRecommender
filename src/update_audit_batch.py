import json
import os

audit_path = r"c:\Users\Greg\Documents\PythonProjects\StatsRecommender\data\expert_audit.json"

with open(audit_path, "r", encoding="utf-8") as f:
    audit = json.load(f)

new_entries = {
    "12497947.json": {
        "title": "Immunogenicity and Safety of a Purified Vero Cell Rabies Vaccine Produced With a Next-Generation Process (PVRV-NG2): A Phase 3 Controlled Randomized Trial",
        "expert_strengths": [
            "Non-inferiority design with justified margin (-5%).",
            "Fixed-sequence method used for multiplicity correction of secondary objectives.",
            "Explicit power calculation (80% power) provided.",
            "ITT (FAS) and Per-protocol (PPAS) populations clearly defined.",
            "Detailed confidence interval methods (Wilson score, Clopper-Pearson) specified."
        ],
        "critical_gaps": [
            "Randomization sequence generation and masking details moved to supplementary materials rather than in main text methods."
        ],
        "overall_rigor": 9
    },
    "12507463.json": {
        "title": "Long-Term Outcomes of Adjuvant Trastuzumab for 9 Weeks or 1 Year for ERBB2-Positive Breast Cancer",
        "expert_strengths": [
            "Post-hoc secondary analysis of a large RCT following CONSORT guidelines.",
            "Central randomization with stratification factors (ER status, nodal status).",
            "Non-inferiority margin and original power calculation specified.",
            "Survival analysis using Kaplan-Meier, log-rank, and Cox proportional hazards with HRs.",
            "Interaction analyses for subgroup variables."
        ],
        "critical_gaps": [
            "P-values unadjusted for multiple testing (exploratory nature acknowledged).",
            "Missing power calculation for the secondary analysis endpoint specifically."
        ],
        "overall_rigor": 8
    },
    "12713889.json": {
        "title": "Sleep disturbances and psychopathology in children/adolescents",
        "expert_strengths": [
            "Large sample size (N=13,472) with Cronbach's alpha reported for scaling.",
            "Split-sample approach (S1/S2) to ensure reproducibility of findings.",
            "Multiple imputation (SPSS) used to handle non-random missing data.",
            "Hierarchical regression models used to disaggregate effects across 5 blocks.",
            "Interaction effects investigated using PROCESS macro with mean centering."
        ],
        "critical_gaps": [
            "No formal sample size/power calculation mentioned for this secondary analysis.",
            "Multiplicity correction for multiple model blocks and interaction terms not detailed."
        ],
        "overall_rigor": 8
    },
    "12727072.json": {
        "title": "BRIDGE platform for dementia research in Korea",
        "expert_strengths": [
            "Comprehensive data management and validation system (DVS) with statistician oversight.",
            "Use of Data Quality Index (DQI) for continuous monitoring of data defects.",
            "ANOVA for continuous and Chi-square for categorical data with Kruskal-Wallis for non-normal distributions.",
            "Comparison with general population (KNHANES) using matching process.",
            "Specific software versions cited (SAS EG 7.1, R 4.1.2)."
        ],
        "critical_gaps": [
            "Power calculation missing for the platform's primary cohort objectives.",
            "Strategy for handling missing data (especially in imaging/PET) not described."
        ],
        "overall_rigor": 7
    },
    "12721701.json": {
        "title": "Salivary parameters, oral health, and adiposity in children",
        "expert_strengths": [
            "Intra- and inter-examiner reproducibility assessed with ICC.",
            "Normality testing (Shapiro-Wilk) and appropriate data transformation (log/sqrt) used.",
            "Appropriate tests for data distribution (t-test vs Mann-Whitney).",
            "Spearman's correlation used to assess multicollinearity among parameters.",
            "Logistic regression models with separate inclusion of collinear variables."
        ],
        "critical_gaps": [
            "Sample size justification/power calculation missing.",
            "Variables in logistic regression blocks need more detailed definition."
        ],
        "overall_rigor": 7
    },
    "12735295.json": {
        "title": "Critical consciousness, social networks, and mental health in adolescents",
        "expert_strengths": [
            "Validated scales (PHQ-4, Flourishing) with reported internal reliability (alpha).",
            "Egocentric network features (degree, density) used in OLS regression.",
            "Assumptions of linear regression (normality of residuals, etc.) explicitly tested.",
            "Robustness check using disaggregated mental health components.",
            "Stepwise regression procedures with standardized continuous variables."
        ],
        "critical_gaps": [
            "Potential for confounding due to multicollinearity (addressed via separate models but limits integration).",
            "No power analysis provided for the complex network effects."
        ],
        "overall_rigor": 7
    },
    "12713947.json": {
        "title": "Emotion regulation and insomnia with psychiatric comorbidity",
        "expert_strengths": [
            "Structured clinical screening (MINI) and balanced group design (n=25/group).",
            "Extensive use of validated scales with current-sample reliability (alpha) reported.",
            "Bonferroni correction used for post-hoc tests after ANOVA.",
            "Effect sizes (Cohen's d) reported for all significant group differences."
        ],
        "critical_gaps": [
            "Small sample size per group (n=25) without power calculation.",
            "Normality assumption for ANOVA not explicitly verified."
        ],
        "overall_rigor": 8
    }
}

audit.update(new_entries)

with open(audit_path, "w", encoding="utf-8") as f:
    json.dump(audit, f, indent=2)

print(f"Updated expert_audit.json. Total entries: {len(audit)}")
