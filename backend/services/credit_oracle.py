import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from google import generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    logger.warning("Google Generative AI not installed. Run: pip install google-generativeai")

class CreditOracle:
    """
    AI-powered explanation generator for credit decisions.
    Powered by Google Gemini (AI Studio – free tier).
    """

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")

        if HAS_GEMINI and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                self.enabled = True
                logger.info("✨ Credit Oracle ENABLED")
            except Exception as e:
                self.enabled = False
                logger.error(f"Failed to initialize Gemini: {e}")
        else:
            self.enabled = False
            logger.warning("⚠️ Credit Oracle DISABLED")
            logger.warning("   Set GOOGLE_API_KEY in .env to enable")

    # ========= CORE UTILITY =========

    def _generate(self, prompt: str, temperature: float = 0.7) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": 1000
                }
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return ""

    # ========= CREDIT DECISION =========

    def explain_decision(
        self,
        client_data: Dict[str, Any],
        similar_clients: List[Any],
        decision: str,
        confidence: float,
        repaid_count: int = 0,
        total_count: int = 0
    ) -> str:

        archetype = client_data.get("archetype", "worker")
        employment = client_data.get("employment_type", "informal")
        years = client_data.get("years_active", 0)
        debt = client_data.get("debt_ratio", 0.5)
        income = client_data.get("monthly_income", 0)
        income_stability = client_data.get("income_stability", 0.5)
        payment_regularity = client_data.get("payment_regularity", 0.5)

        # Handle both dict and Qdrant result objects
        repaid = repaid_count
        if repaid == 0:
            repaid = sum(1 for c in similar_clients if isinstance(c, dict) and c.get("outcome") == "approved")
        
        total = total_count if total_count > 0 else len(similar_clients)
        rejected = total - repaid

        prompt = f"""
You are a compassionate credit analyst at a microfinance institution in Tunisia.
do not mention the response nor use quotation marks in your response.
APPLICANT PROFILE:
- Occupation: {archetype.replace('_', ' ')}
- Employment type: {employment}
- Years active: {years:.1f}
- Debt ratio: {debt:.1%}
- Similar past cases: {repaid} approved, {rejected} not approved out of {total}

DECISION: {decision.upper()}
Confidence: {confidence:.1%}

Write 2 short sentences that:
- Feel human and empathetic
- Explain the decision using similar past cases
- If rejected, offer hope and concrete next steps
- Use “we found”, not “the system decided”
- Simple language, basic financial literacy
"""

        text = self._generate(prompt, temperature=0.7)
        return text if text else self._fallback_explanation(decision, confidence)

    # ========= FRAUD EXPLANATION =========

    def explain_fraud(
        self,
        fraud_score: float,
        fraud_type: str,
        similar_frauds: List[Dict[str, Any]],
        fraud_indicators: List[str]
    ) -> str:

        if not self.enabled:
            return self._fallback_fraud(fraud_score, fraud_type)

        indicators = ", ".join(fraud_indicators[:3]) if fraud_indicators else "unusual patterns"

        prompt = f"""
You are a professional fraud analyst.

Fraud score: {fraud_score:.1%}
Pattern type: {fraud_type.replace('_', ' ')}
Similar fraud cases: {len(similar_frauds)}
Key indicators: {indicators}

Generate a short 2 phrases professional alert that:
- Explains the concern clearly
- Mentions red flags
- Recommends verification steps
- Is firm but not accusatory
"""

        text = self._generate(prompt, temperature=0.5)
        return text if text else self._fallback_fraud(fraud_score, fraud_type)

    # ========= IMPROVEMENT PATH =========

    def generate_improvement_path(
        self,
        original_data: Dict[str, Any],
        modifications: Dict[str, float],
        risk_change: Dict[str, str]
    ) -> List[str]:

        if not self.enabled:
            return self._fallback_improvement(modifications)

        changes = []
        for k, v in modifications.items():
            if v != 0:
                changes.append(f"{k.replace('_', ' ')}: {'+' if v > 0 else ''}{v}")

        prompt = f"""
You are a financial advisor helping an informal worker qualify for credit.

Current debt ratio: {original_data.get('debt_ratio', 0):.1%}
Years active: {original_data.get('years_active', 0):.1f}
Income stability: {original_data.get('income_stability', 0):.1%}
Risk change: {risk_change.get('from')} → {risk_change.get('to')}

Required improvements:
{', '.join(changes)}

Give 3–4 bullet-point steps as a numbered list (1. 2. 3. etc).
Each step must:
- Be realistic for informal workers
- Include a timeline (e.g. 3–6 months)
- Be concrete and measurable
- Use *word* format only for words you want emphasized, which will be converted to bold
Do NOT include arrows, dashes, or Important Notes sections.
Just provide numbered steps only.
"""

        text = self._generate(prompt, temperature=0.6)

        import re
        
        steps = []
        # Split by "Step X:" pattern to group all lines for each step
        step_blocks = re.split(r'(?:^|\n)(?:Step\s+\d+:|Step\s+\d+\s+[-:])', text, flags=re.MULTILINE)
        
        for block in step_blocks:
            if not block.strip():
                continue
            
            # Take the first line or first meaningful content as the step
            lines = block.strip().split('\n')
            
            # Combine multiple lines into a single step description
            combined_text = ' '.join(line.strip() for line in lines if line.strip())
            
            if combined_text:
                # Remove leading bullet points or asterisks
                combined_text = re.sub(r'^[\s*\-•]+', '', combined_text)
                
                # Clean up extra asterisks and whitespace
                combined_text = combined_text.replace('**', '*').strip()
                
                if combined_text:
                    steps.append(combined_text)
        
        # If we only got a few steps, try alternative parsing
        if len(steps) < 3:
            steps = []
            # Alternative: split by any "What to do:" or similar markers
            current_step = []
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if this starts a new step section
                if any(marker in line for marker in ['What to do:', 'Measurable', 'Why it helps:', 'Step']):
                    if current_step:
                        combined = ' '.join(current_step)
                        combined = re.sub(r'^[\s*\-•]+', '', combined)
                        combined = combined.replace('**', '*').strip()
                        if combined:
                            steps.append(combined)
                        current_step = []
                
                if line and not line.startswith('*'):
                    current_step.append(line)
            
            # Add the last step
            if current_step:
                combined = ' '.join(current_step)
                combined = re.sub(r'^[\s*\-•]+', '', combined)
                combined = combined.replace('**', '*').strip()
                if combined:
                    steps.append(combined)
        
        # Ensure we have steps, fallback if needed
        if not steps or (len(steps) == 1 and len(steps[0]) < 20):
            return self._fallback_improvement(modifications)
        
        return steps

    # ========= FALLBACKS =========

    def _fallback_explanation(self, decision: str, confidence: float, repaid: int = 0, total: int = 0) -> str:
        if decision == "approve":
            if total > 0:
                return f"We're pleased with your application. Based on {repaid} out of {total} similar clients in our records who were approved, you meet our lending criteria. Your payment history and income stability give us confidence in approving your request."
            return f"Based on our analysis, we approved your request with {int(confidence * 100)}% confidence."
        else:
            if total > 0 and repaid > 0:
                return f"Thank you for your application. While {repaid} of {total} similar clients in our records were successful, we'd like to see stronger financial indicators. We recommend improving your income stability or reducing your debt ratio, and we're ready to help you achieve that."
            return "We need to see stronger financial indicators before approval, and we're ready to help you improve. Consider reducing your debt or stabilizing your income, and reapply soon."

    def _fallback_fraud(self, score: float, fraud_type: str) -> str:
        if score > 0.9:
            return f"High fraud risk detected matching known {fraud_type.replace('_', ' ')} patterns."
        return "Potential fraud pattern detected. Additional verification is required."

    def _fallback_improvement(self, modifications: Dict[str, float]) -> List[str]:
        steps = []
        if modifications.get("debt_ratio", 0) < 0:
            steps.append("Reduce outstanding debt by 10–15% within 3–6 months")
        if modifications.get("income_stability", 0) > 0:
            steps.append("Stabilize income by documenting regular revenue")
        if not steps:
            steps.append("Continue building your financial history")
        return steps


# ========= SINGLETON =========

_oracle_instance = None

def get_oracle() -> CreditOracle:
    global _oracle_instance
    if _oracle_instance is None:
        _oracle_instance = CreditOracle()
    return _oracle_instance
