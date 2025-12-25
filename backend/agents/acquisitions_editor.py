"""
Acquisitions Editor - Market Assessment & Editorial Vision
First stage in professional publishing workflow
"""

from typing import List, Dict
from agents.base import Agent
from core.style_sheet import StyleSheet
from core.llm_client import LLMClient


class AcquisitionsEditor(Agent):
    """
    Acquisitions Editor - Market Assessment & Vision
    
    This is the FIRST agent in the professional workflow.
    
    Function: They don't fix typos; they buy the book.
    
    Deliverables:
    - Editorial Letter (3-6 page high-level critique)
    - P&L Assessment (Profit & Loss)
    - Comparable titles (comps)
    - Target audience
    - Market positioning
    
    Uses: Claude Opus 4 (premium - needs strategic thinking)
    """
    
    def __init__(self, llm_client: LLMClient):
        super().__init__("acquisitions", llm_client)
    
    def execute(self, manuscript_text: str, style_sheet: StyleSheet) -> Dict:
        """
        Generate market assessment and editorial vision.
        
        Args:
            manuscript_text: Full manuscript
            style_sheet: Style Sheet with metadata
            
        Returns:
            Dictionary with editorial letter, P&L, comps, etc.
        """
        print(f"📊 Acquisitions Editor: Assessing market potential...")
        
        # Generate Editorial Letter
        editorial_letter = self._generate_editorial_letter(manuscript_text, style_sheet)
        
        # Generate P&L Assessment
        p_and_l = self._generate_p_and_l(manuscript_text, style_sheet)
        
        # Identify comparable titles
        comps = self._identify_comps(manuscript_text, style_sheet)
        
        # Define target audience
        target_audience = self._define_target_audience(manuscript_text, style_sheet)

        # Generate Marketing Blurb (Sales Copy)
        marketing_blurb = self._generate_marketing_blurb(manuscript_text, style_sheet)

        # Generate Professional Synopsis (Full Story)
        synopsis = self._generate_professional_synopsis(manuscript_text, style_sheet)
        
        print(f"✅ Acquisitions Editor: Assessment complete")
        
        return {
            "editorial_letter": editorial_letter,
            "p_and_l": p_and_l,
            "comps": comps,
            "target_audience": target_audience,
            "marketing_blurb": marketing_blurb,
            "synopsis": synopsis,
            "recommendation": self._make_recommendation(p_and_l)
        }

    def _generate_editorial_letter(self, text: str, style_sheet: StyleSheet) -> str:
        """Generate a professional editorial letter"""
        
        prompt = f"""You are a senior acquisitions editor at a top publishing house.
        
Write a formal Editorial Letter (3-5 pages) assessing this manuscript.

MANUSCRIPT DETAILS:
- Title: {style_sheet.title or "Untitled"}
- Genre: {style_sheet.genre or "Unknown"}
- Word Count: {style_sheet.word_count:,} words

MANUSCRIPT TEXT:
{text}

STRUCTURE:
1. **The Hook & Market Appeal**: What makes this book special? Why will it sell?
2. **Strengths**: Character depth, plot twists, pacing, voice.
3. **Weaknesses/Developmental Needs**: Pacing issues, plot holes, weak character motivations.
4. **The Verdict**: A clear recommendation on whether to acquire or pass, and why.

TONE: Professional, encouraging but honest, industry-focused.
"""
        return self.generate(prompt, max_tokens=6000, temperature=0.7)

    def _generate_marketing_blurb(self, text: str, style_sheet: StyleSheet) -> str:
        """Generate a catchy marketing blurb (back cover copy)"""
        
        prompt = f"""You are a professional copywriter for a major publishing house.

Write a compelling, sales-oriented marketing blurb (back cover copy) for this book.

MANUSCRIPT DETAILS:
- Title: {style_sheet.title or "Untitled"}
- Genre: {style_sheet.genre or "Unknown"}

SAMPLE TEXT:
{text[:10000]}

REQUIREMENTS:
1. Hook the reader immediately.
2. Introduce the protagonist and the central conflict.
3. Raise the stakes.
4. End with a cliffhanger or intriguing question.
5. Keep it punchy and dramatic (150-250 words).

MARKETING BLURB:
"""
        return self.generate(prompt, max_tokens=500, temperature=0.7)

    def _generate_professional_synopsis(self, text: str, style_sheet: StyleSheet) -> str:
        """Generate a comprehensive, professional synopsis (internal document)"""
        
        prompt = f"""You are an expert editorial assistant writing a formal Story Bible Synopsis.

Write a **PROFESSIONAL SYNOPSIS** (800-1200 words) for this manuscript.

MANUSCRIPT DETAILS:
- Title: {style_sheet.title or "Untitled"}
- Genre: {style_sheet.genre or "Unknown"}
- Word Count: {style_sheet.word_count:,} words

MANUSCRIPT TEXT:
{text}

***CRITICAL REQUIREMENTS (READ CAREFULLY):***
1. **NO INTERNAL MONOLOGUE**: Do NOT output <thinking> tags or any internal reasoning. Start directly with the synopsis content.
2. **THIRD-PERSON PRESENT TENSE**: Write as if it is happening NOW (e.g., "John walks," not "John walked").
3. **REVEAL THE ENDING**: This is NOT a back-cover blurb. You MUST reveal the climax, the resolution, and the final state of the characters.
4. **NARRATIVE ARC**: Structure your synopsis to cover:
   - **Inciting Incident**: What sets the plot in motion?
   - **Rising Action**: Key conflicts and turning points.
   - **Climax**: The peak of the conflict.
   - **Falling Action**: The aftermath.
   - **Resolution**: How the story ends.
5. **FOCUS ON CHARACTER ARCS**: Show how the protagonist changes internally, not just external events.
6. **NO FLUFF**: Do not use "teaser" language like "Will they survive?" State clearly whether they survive or not.

FORMAT:
Use Markdown headers for sections:
# PROFESSIONAL SYNOPSIS
## [Title]
**Genre:** [Genre]
---
### Overview
[1 paragraph summary of the premise]
---
### Act One: The Assignment
[Detailed summary of the beginning]

### Act Two: The Complication
[Detailed summary of the middle]

### Act Three: The Resolution
[Detailed summary of the ending, INCLUDING SPOILERS]
"""
        
        response = self.generate(prompt, max_tokens=8000, temperature=0.4)
        
        # Clean up any <thinking> blocks if the model included them (handling unclosed tags)
        import re
        # Remove <thinking>...</thinking> OR <thinking>... (end of string)
        response = re.sub(r'<thinking>.*?(?:</thinking>|$)', '', response, flags=re.DOTALL).strip()
        
        return response
    
    def _generate_p_and_l(self, text: str, style_sheet: StyleSheet) -> Dict:
        """Generate Profit & Loss assessment"""
        
        prompt = f"""You are a publishing financial analyst.

Generate a P&L (Profit & Loss) assessment for this manuscript.

MANUSCRIPT:
- Genre: {style_sheet.genre or "Unknown"}
- Word Count: {style_sheet.word_count:,}
- Target Audience: {style_sheet.target_audience or "TBD"}

SAMPLE TEXT:
{text[:5000]}

Provide estimates in JSON format:
{{
  "estimated_advance": 50000,
  "print_run_first_edition": 10000,
  "estimated_retail_price": 16.99,
  "production_cost_per_unit": 3.50,
  "marketing_budget": 25000,
  "projected_first_year_sales": 8000,
  "break_even_units": 5500,
  "profit_potential": "moderate",
  "risk_level": "low",
  "notes": "Strong commercial appeal in growing genre"
}}

Be realistic based on current market conditions.
"""
        
        response = self.generate(prompt, max_tokens=1000, temperature=0.3)
        
        try:
            return self.parse_json_response(response)
        except:
            return {"error": "Failed to parse P&L", "raw": response}
    
    def _identify_comps(self, text: str, style_sheet: StyleSheet) -> List[Dict]:
        """Identify comparable titles"""
        
        prompt = f"""You are a publishing market analyst.

Identify 5 comparable titles (comps) for this manuscript.

MANUSCRIPT:
- Genre: {style_sheet.genre or "Unknown"}

SAMPLE:
{text[:5000]}

Return JSON array of comps:
[
  {{
    "title": "The Night Circus",
    "author": "Erin Morgenstern",
    "year": 2011,
    "sales": "3 million+",
    "why_comparable": "Similar magical realism tone and structure",
    "market_position": "Literary fantasy crossover"
  }}
]

Choose recent bestsellers (last 10 years) that readers of THIS book would also enjoy.
"""
        
        response = self.generate(prompt, max_tokens=1500, temperature=0.5)
        
        try:
            return self.parse_json_response(response)
        except:
            return []
    
    def _define_target_audience(self, text: str, style_sheet: StyleSheet) -> Dict:
        """Define target audience"""
        
        prompt = f"""You are a publishing marketing strategist.

Define the target audience for this manuscript.

MANUSCRIPT:
- Genre: {style_sheet.genre or "Unknown"}

SAMPLE:
{text[:5000]}

Return JSON:
{{
  "primary_audience": "Women 25-45",
  "secondary_audience": "Book club readers",
  "demographics": {{
    "age_range": "25-55",
    "gender_split": "80% female, 20% male",
    "education": "College-educated",
    "income": "Middle to upper-middle class"
  }},
  "psychographics": {{
    "interests": ["Literary fiction", "Historical drama", "Strong female characters"],
    "reading_habits": "2-3 books per month",
    "purchase_drivers": ["Word of mouth", "Book club picks", "NPR reviews"]
  }},
  "comp_readers": ["Fans of Celeste Ng", "Readers of The Nightingale"]
}}
"""
        
        response = self.generate(prompt, max_tokens=1000, temperature=0.5)
        
        try:
            return self.parse_json_response(response)
        except:
            return {"error": "Failed to parse audience"}
    
    def _make_recommendation(self, p_and_l: Dict) -> str:
        """Make acquire/pass recommendation"""
        
        if "error" in p_and_l:
            # Even if P&L parsing failed, provide a constructive recommendation
            return "CONSIDER FOR ACQUISITION - Editorial review recommended. Financial projections require manual assessment."
        
        profit_potential = p_and_l.get("profit_potential", "unknown")
        risk_level = p_and_l.get("risk_level", "unknown")
        
        if profit_potential in ["high", "very_high"] and risk_level in ["low", "moderate"]:
            return "ACQUIRE - Strong commercial potential"
        elif profit_potential == "moderate" and risk_level == "low":
            return "ACQUIRE - Solid mid-list title"
        elif profit_potential == "low" or risk_level == "high":
            return "PASS - Insufficient commercial potential"
        else:
            return "CONSIDER FOR ACQUISITION - Needs further market analysis"
