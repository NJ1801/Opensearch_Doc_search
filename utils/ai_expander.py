# utils/ai_expander.py

import os
import google.generativeai as genai


MAX_EXPANSIONS = 5  # HARD LIMIT – never increase casually


def expand_with_ai(keyword: str) -> str:
    """
    Expand medical abbreviations / synonyms using Gemini.
    Returns a comma-separated STRING.
    Always includes the original keyword.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # AI disabled or misconfigured
        return keyword

    try:
        genai.configure(api_key=api_key)

        prompt = f"""
        The user entered a medical term or abbreviation: "{keyword}"

        Return up to {MAX_EXPANSIONS} related terms:
        - full forms
        - abbreviations
        - Top common medical synonyms

        Rules:
        - Output ONLY a comma-separated list
        - No explanations
        - Include the original term
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        raw = response.text.strip()

        parts = [p.strip() for p in raw.split(",") if p.strip()]

        # Deduplicate + preserve order
        seen = set()
        cleaned = []
        for p in parts:
            key = p.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append(p)

        # Guarantee original keyword is first
        if keyword.lower() not in seen:
            cleaned.insert(0, keyword)

        # Enforce hard limit
        cleaned = cleaned[:MAX_EXPANSIONS]

        return ", ".join(cleaned)

    except Exception:
        # Absolute safety fallback
        return keyword
