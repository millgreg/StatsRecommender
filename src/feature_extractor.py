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
            "sample_size": [r"(?i)n\s*=\s*\d+", r"(?i)sample size", r"(?i)total of \d+", r"(?i)enrolled \d+", r"(?i)power calculation", r"(?i)power analysis", r"(?i)approximate", r"(?i)initially calculated"],
            "randomization": [r"(?i)randomized", r"(?i)randomisation", r"(?i)randomly assigned", r"(?i)randomly allocated", r"(?i)stratified"],
            "blinding": [r"(?i)blinded", r"(?i)blinding", r"(?i)double-blind", r"(?i)masking", r"(?i)masked", r"(?i)allocation concealment"],
            "allocation_concealment": [r"(?i)allocation concealment", r"(?i)sequentially numbered", r"(?i)opaque envelopes", r"(?i)central(ized)? randomisation", r"(?i)concealed allocation"],
            "interaction_subgroup": [r"(?i)interaction (effect|test|term)", r"(?i)subgroup analysis", r"(?i)stratified analysis", r"(?i)heterogeneity of treatment", r"(?i)post-hoc subgroup"],

            
            # Category: Variables & Measures
            "variable_definitions": [r"(?i)centrally determined", r"(?i)central laboratory", r"(?i)immunohistochemical analysis", r"(?i)standardized assessment", r"(?i)endpoint definition", r"(?i)outcome measure"],
            
            # Category: Analysis Principles & Frameworks
            "analysis_principles": [r"(?i)intention-to-treat", r"(?<![a-zA-Z])ITT(?![a-zA-Z])", r"(?i)per-protocol", r"(?i)modified ITT", r"(?i)completer analysis"],
            "itt_details": [r"(?i)intention-to-treat (analysis|approach|population)", r"(?i)analyzed based on initial assignment", r"(?i)all patients who were randomised"],

            "software": [r"(?<![a-zA-Z])SAS(?![a-zA-Z])", r"(?i)R version \d+", r"(?i)GraphPad Prism", r"(?<![a-zA-Z])SPSS(?![a-zA-Z])", r"(?i)Stata( version \d+)?", r"(?i)Python \d+", r"(?i)Matlab"],
            "error_measures": [r"(?i)standard deviation", r"(?<![a-zA-Z])sd(?![a-zA-Z])", r"(?i)standard error", r"(?<![a-zA-Z])sem(?![a-zA-Z])", r"(?i)interquartile range", r"(?<![a-zA-Z])iqr(?![a-zA-Z])"],
            "multiplicity_correction": [r"(?i)bonferroni", r"(?i)benjamini-hochberg", r"(?i)false discovery rate", r"(?i)multiple (comparisons|testing)", r"(?i)adjustment for multiplicity", r"(?i)tukey", r"(?i)scheff."],
            "normality_checks": [r"(?i)\bshapiro-wilk\b", r"(?i)\bkolmogorov-smirnov\b", r"(?i)\bnormality (test|check)\b", r"(?i)\bskewness\b", r"(?i)\bkurtosis\b", r"(?i)\bqq-plot\b", r"(?i)\bquantile-quantile\b"],
            
            # Statistical Methods (General)
            "p_values": [r"(?i)p\s*[=<>]\s*\d+\.\d+", r"(?i)p-value", r"(?i)significance level", r"(?i)alpha"],
            "confidence_intervals": [r"(?i)95%\s*ci", r"(?i)confidence interval", r"(?i)95%\s*confidence"],
            "comparative_stats": [r"(?i)t-test", r"(?i)chi-square", r"(?i)fisher['\u2019]s exact", r"(?i)mann-whitney", r"(?i)wilcoxon", r"(?i)odds ratio", r"(?i)relative risk"],
            "non_parametric": [r"(?i)non-parametric", r"(?i)permutation test", r"(?i)bootstrapping", r"(?i)kruskal-wallis", r"(?i)signed-rank"],
            "advanced_modeling": [r"(?i)gee", r"(?i)generalized estimating equations", r"(?i)bayesian", r"(?i)propensity score", r"(?i)sensitivity analysis", r"(?i)multiple imputation", r"(?i)linear mixed model", r"(?<![a-zA-Z])LMM(?![a-zA-Z])", r"(?<![a-zA-Z])GLMM(?![a-zA-Z])", r"(?i)repeated measures anova"],
            "assumption_checks": [r"(?i)schoenfeld residuals", r"(?i)proportional hazards assumption", r"(?i)normality check", r"(?i)homoscedasticity", r"(?i)collinearity"],
            "survival_analysis": [r"(?i)kaplan-meier", r"(?i)log-rank", r"(?i)hazard ratio", r"(?<![a-zA-Z])HR\s*=(?![a-zA-Z])", r"(?i)median survival"],
            "regression_and_models": [r"(?i)cox proportional", r"(?i)logistic regression", r"(?i)linear model", r"(?i)mixed-effect", r"(?i)ancova", r"(?i)anova"],
            "reporting_guidelines": [r"(?<![a-zA-Z])CONSORT(?![a-zA-Z])", r"(?<![a-zA-Z])PRISMA(?![a-zA-Z])", r"(?i)STROBE", r"(?i)ARRIVE", r"(?i)SPIRIT", r"(?<![a-zA-Z])GRDI(?![a-zA-Z])", r"(?i)Guidelines for Research Data Integrity"],
            
            # Category: Data Properties & Dependency
            "data_types": [r"(?i)categorical", r"(?i)continuous", r"(?i)binary", r"(?i)ordinal", r"(?i)proportions", r"(?i)frequencies"],
            "dependency": [r"(?i)paired\s+(data|t-test|analysis|samples|design|measures|subjects)", r"(?i)matched\s+(pairs|comparison|analysis|controls|case-control)", r"(?i)repeated measures", r"(?i)longitudinal", r"(?i)within-subject"],
            "clustering": [r"(?i)cluster", r"(?i)nested", r"(?i)hierarchical", r"(?i)multilevel", r"(?i)unit of analysis", r"(?i)intra-class correlation", r"(?<![a-zA-Z])ICC(?![a-zA-Z])"],
            
            # Category: Quality & Effect Measures
            "missing_data": [r"(?i)missing values", r"(?i)dropout", r"(?i)imputation", r"(?i)loss to follow-up"],
            "effect_size": [r"(?i)effect size", r"(?i)mean difference", r"(?i)absolute risk reduction", r"(?i)number needed to treat", r"(?i)standardized mean difference", r"(?i)cohen.s d"],
            "post_hoc": [r"(?i)post-hoc", r"(?i)post hoc", r"(?i)multiple comparisons", r"(?i)tukey", r"(?i)scheff.", r"(?i)sidak", r"(?i)dunn", r"(?i)newman-keuls"],
            "baseline_reporting": [r"(?i)baseline (characteristic|demographic|profile|data)", r"(?i)table 1"],
            
            # Systematic Review / Advanced Modeling
            "advanced_modeling_extra": [r"(?i)cubic spline", r"(?i)restricted cubic spline", r"(?i)nonlinear effects", r"(?i)splines"],
            "systematic_review_metrics": [r"(?<![a-zA-Z])SUCRA(?![a-zA-Z])", r"(?i)surface under the cumulative ranking", r"(?i)rankogram", r"(?i)deviance information criterion", r"STRICT:DIC", r"(?i)node-splitting"]
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
                "examples": found[:3] # Show first 3 examples
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
            full_text = ""
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
