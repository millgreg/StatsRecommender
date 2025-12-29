import json
import os
import openai
from dotenv import load_dotenv
from rule_based_feedback import RuleBasedFeedbackEngine

load_dotenv()

class FeedbackGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
        self.rule_engine = RuleBasedFeedbackEngine()

    def generate_feedback(self, title, original_text, features):
        """
        Generates feedback using a deterministic rule engine and optionally an LLM.
        """
        # 1. Generate Deterministic Baseline
        rule_feedback = self.rule_engine.generate_feedback(features)
        
        if not self.api_key:
            return {
                "note": "OPENAI_API_KEY not found. Showing deterministic audit only.",
                "deterministic_baseline": rule_feedback,
                "overall_score": rule_feedback["overall_score"],
                "rigor_rating": rule_feedback["rigor_rating"],
                "critical_gaps": rule_feedback["critical_gaps"],
                "strengths": rule_feedback["strengths"],
                "actionable_recommendations": rule_feedback["actionable_recommendations"]
            }

        # 2. Enhance with LLM if API key is available
        prompt = f"""
        You are an elite statistical reviewer for top-tier medical journals (e.g., Nature, NEJM, The Lancet).
        Your goal is to perform a high-rigor audit of the 'Methods' section provided below.
        
        ### AUDIT CRITERIA
        1. **Statistical Assumptions (CRITICAL):** 
           - Look for explicit confirmation of assumptions (e.g., Normality for t-tests/ANOVA, Proportional Hazards for Cox regression).
           - If a parametric test is used without mentioning normality checks or if data transformation isn't discussed for skewed data, flag this as a major reporting gap.
           - Check for homoscedasticity or collinearity assessments if applicable.
        2. **Multiplicity Correction:**
           - If multiple primary endpoints, multiple subgroups, or multiple time points are analyzed, is there an adjustment (Bonferroni, FDR, etc.)?
           - If no adjustment is made, explain why it's a risk for Type I error.
        3. **Study Design & Transparency:**
           - Blinding: Is it described in detail (who, how, which phase)? "Single-blinded" without process details is LOW quality.
           - Randomization: Is the sequence generation and allocation concealment described?
           - Sample Size: Is there a formal power calculation? If "approximate" or "estimated," flag for lack of precision.
        4. **Analysis Principles:**
           - ITT/Per-Protocol: Is the choice clearly stated and justified?
           - Software: Specific versions and packages must be cited.

        Article Title: {title}
        
        ### Extracted Features Summary (from deterministic audit):
        {json.dumps(features, indent=2)}
        
        ### Original Text Excerpt:
        {original_text[:8000]}...

        ### OUTPUT FORMAT (JSON ONLY)
        Provide feedback in the following format:
        {{
            "overall_score": 1-10,
            "rigor_rating": "High/Medium/Low",
            "critical_gaps": ["List specific missing checks or reporting flaws"],
            "strengths": [],
            "weaknesses": [],
            "foundational_rigor_audit": {{
                "assumptions_handling": "Detailed assessment of how they handled/reported assumptions",
                "multiplicity_handling": "Assessment of multiple testing adjustments",
                "transparency_rating": "Rating of blinding/randomization details"
            }},
            "actionable_recommendations": [
                {{
                    "item": "Specific Section",
                    "issue": "Specific reporting or statistical flaw",
                    "recommendation": "Technical fix"
                }}
            ],
            "nature_adherence_score": 1-10
        }}
        """

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            llm_feedback = json.loads(response.choices[0].message.content)
            # Merge or keep both
            return {
                "deterministic_baseline": rule_feedback,
                "llm_enhanced_feedback": llm_feedback
            }
        except Exception as e:
            return {
                "error": f"LLM Error: {str(e)}",
                "deterministic_baseline": rule_feedback
            }

def process_features(features_folder="data/features", processed_folder="data/processed", output_folder="data/feedback"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    generator = FeedbackGenerator()
    
    for filename in os.listdir(features_folder):
        if filename.endswith(".json"):
            # Load features
            with open(os.path.join(features_folder, filename), "r", encoding="utf-8") as f:
                feature_data = json.load(f)
            
            # Load original text for context
            with open(os.path.join(processed_folder, filename), "r", encoding="utf-8") as f:
                processed_data = json.load(f)
            
            full_text = ""
            for m in processed_data.get("methods", []):
                full_text += m.get("content", "") + "\n"
            
            print(f"Generating feedback for: {filename}")
            feedback = generator.generate_feedback(
                feature_data.get("title"),
                full_text,
                feature_data.get("features")
            )
            
            output_data = {
                "title": feature_data.get("title"),
                "pmcid": feature_data.get("pmcid"),
                "features": feature_data.get("features"),
                "feedback": feedback
            }
            
            output_path = os.path.join(output_folder, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved feedback to: {output_path}")

if __name__ == "__main__":
    process_features()
