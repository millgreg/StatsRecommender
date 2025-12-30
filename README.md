# Automated Feedback on Statistical Reporting (AFSR)

AFSR is a local, reproducible feedback system designed to analyze the **Methods** sections of scientific papers, specifically focusing on statistical reporting quality. It provides structured, actionable feedback to help researchers improve the transparency and rigor of their reporting.

## Core Features

- **Automated Feature Extraction**: Uses NLP and regex to identify key statistical elements (tests, software, sample size, p-values, normality checks, etc.).
- **Deterministic Rule Engine**: Audits extracted features against "Gold Standard" reporting criteria (inspired by CONSORT, ARRIVE, and Nature guidelines).
- **LLM-Enhanced Insights**: (Optional) Uses GPT-4o to provide deep-dive qualitative feedback on statistical assumptions and analysis principles.
- **Reproducible Pipeline**: Full traceability from PMC extraction to final feedback.

## Installation

Ensure you have [Conda](https://docs.conda.io/en/latest/) installed, then run:

```bash
conda env create -f environment.yml
conda activate stats_rec_env
```

## Usage

### 1. Audit a Single Paper (CLI)

Use the `audit_paper.py` tool to quickly check a local file or raw text.

```bash
# Audit a text file
python src/audit_paper.py --file my_manuscript.txt

# Audit raw text
python src/audit_paper.py --text "We performed a t-test with n=10..."
```

### 2. Batch Processing from PMC

The core pipeline can process papers directly from PubMed Central using their PMCIDs.

1. **Fetch and Process**: Run the fetcher scripts in `src/`.
2. **Generate Dashboard**: 
   ```bash
   python src/generate_dashboard.py
   ```
   This creates a visual summary of the audits in `reports/`.

## Statistical Rigor Standards

AFSR looks for several critical reporting elements, including:

- **Assumptions**: Shapiro-Wilk, Kolmogorov-Smirnov, Normality checks.
- **Multiplicity**: Bonferroni, FDR, adjustment for multiple comparisons.
- **Study Design**: Randomization, Blinding, Power calculations.
- **Analysis**: Intention-to-Treat (ITT) principles, Software versioning.

## Contributing

This project aims to bridge the gap between automated research-quality auditing and domain-specific feedback. We welcome contributions to our rule engine and ground truth datasets.
