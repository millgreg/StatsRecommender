import spacy
import json
import os
import re

# Load SpaCy model (ensure en_core_web_sm is installed or used)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class FeatureExtractor:
    def __init__(self):
        # Initial set of patterns/keywords for CONSORT items
        self.rules = {
            # Category: Study Design & Sampling
            "sample_size": [r"(?i)sample size", r"(?i)power calculation", r"(?<![a-zA-Z])n\s*[=\u2009]\s*\d+(?![a-zA-Z])", r"(?i)total of \d+ participants"],
            "randomization": [r"(?i)randomis(e|ation)", r"(?i)randomized controlled trial", r"(?i)randomly assigned", r"(?i)allocation"],
            "blinding": [r"(?i)blinded", r"(?i)\bmasking\b(?!\s*to\s*(?:peptide|antigen|ligand|receptor|epitope))", r"(?i)masked", r"(?i)unblinded"],
            "allocation_concealment": [r"(?i)concealment", r"(?i)opaque envelopes", r"(?i)sequentially numbered", r"(?i)central randomisation"],
            "interaction_subgroup": [r"(?i)statistical interaction", r"(?i)interaction (effect|term|p-value)", r"(?i)subgroup analysis", r"(?i)stratification", r"(?i)heterogeneity"],
            "variable_definitions": [r"(?i)outcome measure", r"(?i)primary endpoint", r"(?i)variable definition"],
            
            # Category: Analysis Principles & Frameworks
            "analysis_principles": [r"(?i)intention-to-treat", r"(?<![a-zA-Z])ITT(?![a-zA-Z])", r"(?i)per-protocol", r"(?i)modified ITT", r"(?i)completer analysis"],
            "itt_details": [r"(?i)intention-to-treat (analysis|approach|population)", r"(?i)analyzed based on initial assignment", r"(?i)all patients who were randomised"],

            "software": [
                r"(?<![a-zA-Z])SAS(?:[,\s]+(?:version\s+)?\d+\.?\d*)?(?![a-zA-Z])", 
                r"(?<![a-zA-Z])R(?:[,\s]+(?:version\s+)?)(\d+\.\d+\.?\d*)(?![a-zA-Z])", 
                r"(?i)GraphPad Prism(?:\s+\d+)?", 
                r"(?<![a-zA-Z])SPSS(?:\s+Statistics)?(?:[,\s]+(?:version\s+)?\d+)?(?![a-zA-Z])", 
                r"(?i)Stata(?:[,\s]+(?:version\s+)?\d+)?", 
                r"(?i)Python\s+\d+\.?\d*", 
                r"(?i)Matlab", 
                r"(?i)Statistical Analysis Software",
                r"(?i)ImageJ", r"(?i)FlowJo", r"(?i)Seurat", r"(?i)Bioconductor", r"(?i)PyMOL", r"(?i)PhenoGraph", r"(?i)CellProfiler"
            ],
            "error_measures": [r"(?i)standard deviation", r"(?<![a-zA-Z])sd(?![a-zA-Z])", r"(?i)standard error", r"(?<![a-zA-Z])sem(?![a-zA-Z])", r"(?i)interquartile range", r"(?<![a-zA-Z])iqr(?![a-zA-Z])", r"STRICT:SD"],
            "multiplicity_correction": [r"(?i)\bbonferroni\b", r"(?i)\bbenjamini-hochberg\b", r"(?i)false discovery rate", r"(?i)multiple (comparisons|testing)", r"(?i)adjustment for multiplicity", r"(?i)\btukey\b", r"(?i)\bscheff.\b", r"(?i)\bholm\b(?!\s*laser)", r"(?i)\bdunnett\b", r"(?i)\bsidak\b", r"(?i)control the family-wise error", r"(?i)nominal", r"(?i)no (formal )?.*hypothesis testing", r"(?i)no\s+(?:formal\s+)?(?:adjustment|correction|multiplicity)"],
            "normality_checks": [r"(?i)\bshapiro-wilk\b", r"(?i)\bkolmogorov-smirnov\b", r"(?i)\bnormality (test|check)\b", r"(?i)\bskewness\b", r"(?i)\bkurtosis\b", r"(?i)\bqq-plot\b", r"(?i)\bquantile-quantile\b"],
            
            # Statistical Methods (General)
            "p_values": [r"(?i)p\s*[=<>]\s*\d+\.\d+", r"(?i)p-value", r"(?i)significance level", r"(?i)alpha", r"(?i)secondary (end\s*point|outcome)"],
            "confidence_intervals": [r"(?i)95%\s*ci", r"(?i)confidence interval", r"(?i)95%\s*confidence"],
            "comparative_stats": [r"(?i)t-test", r"(?i)chi-square", r"(?i)\bchi2\b", r"(?i)\b\u03c72\b", r"(?i)fisher['\u2019']s exact", r"(?i)mann-whitney", r"(?i)wilcoxon", r"(?i)odds ratio", r"(?i)relative risk", r"(?i)fold-change", r"(?i)titer", r"(?i)permutation test", r"(?i)power spectrum", r"(?i)spectral density"],
            "non_parametric": [r"(?i)non-parametric", r"(?i)permutation test", r"(?i)bootstrapping", r"(?i)kruskal-wallis", r"(?i)signed-rank"],
            "advanced_modeling": [r"(?i)gee", r"(?i)generalized estimating equations", r"(?i)bayesian", r"(?i)propensity score", r"(?i)sensitivity analysis", r"(?i)multiple imputation", r"(?i)linear mixed model", r"(?<![a-zA-Z])LMM(?![a-zA-Z])", r"(?<![a-zA-Z])GLMM(?![a-zA-Z])", r"(?i)repeated measures anova", r"(?i)mixed-effects?", r"(?i)negative binomial", r"(?i)bootstrap(ping)?", r"(?i)cross-validation", r"(?i)random forest", r"(?i)mcmc", r"(?i)markov chain", r"(?i)MNAR", r"(?i)MMRM", r"(?i)pattern mixture model"],
            "assumption_checks": [r"(?i)schoenfeld residuals", r"(?i)proportional hazards assumption", r"(?i)normality check", r"(?i)homoscedasticity", r"(?i)collinearity", r"(?i)assumption check", r"(?i)proportional hazards"],
            "survival_analysis": [r"(?i)kaplan-meier", r"(?i)log-rank", r"(?i)hazard ratio", r"(?<![a-zA-Z])HR\s*[=<>](?![a-zA-Z])", r"(?i)median survival", r"(?i)restricted mean survival", r"(?i)rfs", r"(?i)\boverall survival\b", r"STRICT:OS"],
            "regression_and_models": [r"(?i)cox proportional", r"(?i)logistic regression", r"(?i)linear model", r"(?i)mixed-effect", r"(?i)ancova", r"(?i)anova", r"(?i)multivariable regression"],
            "reporting_guidelines": [r"(?<![a-zA-Z])CONSORT(?![a-zA-Z])", r"(?<![a-zA-Z])PRISMA(?![a-zA-Z])", r"(?i)STROBE", r"(?i)ARRIVE", r"(?i)SPIRIT", r"(?<![a-zA-Z])GRDI(?![a-zA-Z])", r"(?i)Guidelines for Research Data Integrity"],
            
            # Category: Data Properties & Dependency
            "data_types": [r"(?i)categorical", r"(?i)continuous", r"(?i)binary", r"(?i)ordinal", r"(?i)proportions", r"(?i)frequencies"],
            "dependency": [r"(?i)paired\s+(data|t-test|analysis|samples|design|measures|subjects)", r"(?i)matched\s+(pairs|comparison|analysis|controls|case-control)", r"(?i)repeated measures", r"(?i)longitudinal", r"(?i)within-subject"],
            "clustering": [r"(?i)\bcluster(?!\s*(?:of differentiation|of genes|analysis|algorithm|solution))\b", r"(?i)nested", r"(?i)hierarchical", r"(?i)multilevel", r"(?i)unit of analysis", r"(?i)intra-class correlation", r"(?<![a-zA-Z])ICC(?![a-zA-Z])"],
            
            # Category: Quality & Effect Measures
            "missing_data": [r"(?i)missing (values|data|information)", r"(?i)dropout", r"(?i)imputation", r"(?i)loss to follow-up", r"(?i)not imputed", r"(?i)no imputation", r"(?i)complete\s*case", r"(?i)available\s*case"],
            "effect_size": [r"(?i)effect size", r"(?i)odds ratio", r"(?<![a-zA-Z])OR(?![a-zA-Z])", r"(?i)hazard ratio", r"(?<![a-zA-Z])HR(?![a-zA-Z])", r"(?i)relative risk", r"(?<![a-zA-Z])RR(?![a-zA-Z])", r"(?i)mean difference", r"(?i)cohen'?s d", r"(?i)standardized difference"],
            "post_hoc": [r"(?i)post-hoc", r"(?i)post hoc", r"(?i)multiple comparisons", r"(?i)tukey", r"(?i)scheff.", r"(?i)sidak", r"(?i)dunn", r"(?i)newman-keuls"],
            "baseline_reporting": [r"(?i)baseline (characteristic|demographic|profile|data)", r"(?i)table 1"],
            
            # Systematic Review / Advanced Modeling
            "advanced_modeling_extra": [r"(?i)cubic spline", r"(?i)restricted cubic spline", r"(?i)nonlinear effects", r"(?i)splines", r"(?i)recall\s*bias", r"(?i)exclud(?:ed|ing|usion)", r"(?i)deviation from (protocol|plan|pre-specified)", r"(?i)pre-specified", r"(?i)categoriz(?:ed|ation)", r"(?i)crossover", r"(?i)compliance", r"(?i)attrition"],
            "systematic_review_metrics": [r"(?<![a-zA-Z])SUCRA(?![a-zA-Z])", r"(?i)surface under the cumulative ranking", r"(?i)rankogram", r"(?i)deviance information criterion", r"STRICT:DIC", r"(?i)node-splitting", r"(?i)credible interval", r"STRICT:CrI", r"(?i)transitivity", r"(?i)network\s*fragment(?:ed|ation)", r"(?i)I2\s*[=<>]\s*", r"(?i)I-squared", r"(?i)heterogeneity threshold"],
            "diagnostic_metrics": [r"(?i)AUC\s*[=<>]\s*", r"(?i)Nomogram", r"(?i)ROC\b", r"(?i)sensitivity", r"(?i)specificity", r"(?i)positive predictive value", r"(?<![a-zA-Z])PPV(?![a-zA-Z])", r"(?<![a-zA-Z])NPV(?![a-zA-Z])", r"(?i)hosmer-lemeshow"],
            "model_details": [r"(?i)covariance structure", r"(?i)exchangeable", r"(?i)unstructured", r"(?i)auto-regressive", r"(?i)AR\(1\)", r"(?i)compound symmetry"],
            
            # Domain Indicators (Basic Science)
            "domain_indicators": [
                r"(?i)mice", r"(?i)mouse model", r"(?i)cell line", r"(?i)western blot", r"(?i)immunohistochemistry", 
                r"(?i)staining", r"(?i)confocal", r"(?i)microscopy", r"(?i)in vitro", r"(?i)in vivo", 
                r"(?i)transcriptom(e|ics)", r"(?i)knockout", r"(?i)transgenic", r"(?i)fluorescence", 
                r"(?i)quantification", r"(?i)crystallography", r"(?i)flow cytometry"
            ],
        }

    def extract_features(self, text):
        results = {}
        for feature, patterns in self.rules.items():
            found = []
            for pattern in patterns:
                is_strict = pattern.startswith("STRICT:")
                clean_pattern = pattern.replace("STRICT:", "")
                
                if is_strict:
                    # Case-sensitive, exact match with lookarounds
                    regex = r"(?<![a-zA-Z])" + re.escape(clean_pattern) + r"(?![a-zA-Z])"
                    matches = re.finditer(regex, text)
                else:
                    # Standard behavior (already mostly handled by (?i) in rules)
                    matches = re.finditer(clean_pattern, text)
                    
                for m in matches:
                    # Capture context
                    start = max(0, m.start() - 30)
                    end = min(len(text), m.end() + 30)
                    found.append({
                        "match": m.group(),
                        "context": text[start:end].strip().replace("\n", " ")
                    })
            results[feature] = {
                "present": len(found) > 0,
                "count": len(found),
                "unique_matches": list(set(m["match"].lower() for m in found)),
                "examples": found[:3] # Show first 3 examples for readability
            }
        return results

def process_processed_data(processed_folder="data/processed", output_folder="data/features"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    extractor = FeatureExtractor()
    
    for filename in os.listdir(processed_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(processed_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Combine all methods and stats text
            # CRITICAL: Include Title and Abstract (if available) for Domain Detection context
            full_text = data.get("title", "") + "\n\n"
            
            for m in data.get("methods", []):
                full_text += m.get("content", "") + "\n"
            for s in data.get("stats_reproducibility", []):
                full_text += s.get("content", "") + "\n"
            
            if full_text:
                print(f"Extracting features from: {filename}")
                features = extractor.extract_features(full_text)
                
                output_data = {
                    "title": data.get("title"),
                    "pmcid": data.get("pmcid"),
                    "features": features
                }
                
                output_path = os.path.join(output_folder, filename)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2)
                print(f"Saved features to: {output_path}")

if __name__ == "__main__":
    process_processed_data()
