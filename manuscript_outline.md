# Manuscript Outline: Automated Feedback on Statistical Reporting (AFSR)

## Title (Working)
**Scalable, Deterministic Auditing of Statistical Reporting Quality in Biomedical Research: The AFSR System**

## Abstract
- **Background**: Low reproducibility in biomedical research is often linked to poor statistical reporting.
- **Objective**: Develop and validate a non-LLM, rule-based engine to provide real-time, actionable feedback on statistical rigor.
- **Methods**: We implemented a deterministic pipeline for PDF/XML ingestion, feature extraction using tailored regex, and study-type-aware feedback logic.
- **Results**: On a gold-standard dataset of 35 papers, AFSR achieved high sensitivity. In a large-scale audit of 124 papers, the system identified critical gaps, most notably a 55.6% absence of blinding details in clinical trials.
- **Conclusion**: AFSR provides a robust, hallucination-free alternative to LLMs for automated research auditing.

## 1. Introduction
- The reproducibility crisis and the "Methods" section gap.
- Limitations of current tools (Manual review vs. Hallucination-prone LLMs).
- The case for deterministic, category-aware rules.

## 2. Methods
### 2.1 System Architecture
- Data Ingestion: Automated PMC fetching and local PDF parsing.
- Feature Extraction: Multi-layered regex patterns for statistical tests, power, blinding, and data types.
### 2.2 Study Type Detection
- Logic for distinguishing Clinical Trials, Observational Studies, Basic Science, and Non-Research (Reviews/Guidelines).
### 2.3 Feedback Engine
- Gated logic to suppress irrelevant critiques (e.g., no blinding gaps for Survey studies).

## 3. Results
### 3.1 Validation Performance
- Initial Baseline: F1=0.69.
- Final Precision-Refined Performance: Verified on N=20 validation batch with zero false positives for non-research papers.
- Robustness: 100% detection rate across semantic synonyms.
### 3.2 Large-Scale Audit (N=124)
- **Score Distribution**: Bimodal distribution separating high-rigor clinical studies from casual mentions.
- **Gap Prevalence**: 
    - 55.6% Missing Blinding/Masking.
    - 37.9% Missing Power Calculation details.
    - 34.7% P-values reported only as thresholds (P<0.05).

## 4. Discussion
- **The "Bimodal" Rigor Gap**: High-impact vs. Low-impact reporting styles.
- **Comparison with LLMs**: Why deterministic rules matter for scientific precision.
- **Future Directions**: Expansion to Table/Figure data extraction.

## Figures & Tables
- **Figure 1**: Distribution of Statistical Rigor Scores (N=124).
- **Figure 2**: Heatmap of Statistical Gap Prevalence by Study Type.
- **Table 1**: Sensitivity/Robustness test results for key statistical features.
