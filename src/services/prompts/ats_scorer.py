"""ATS quality analysis prompt."""

ATS_QUALITY_PROMPT = """You are an elite technical recruiter evaluating resume quality.

TASK: Evaluate the recruiter readability and quality of this resume. You are NOT calculating ATS score — only evaluating writing quality.

EVALUATE:
1. Bullet point quality (action verbs, specificity)
2. Quantified impact (numbers, percentages, scale)
3. Clarity and conciseness
4. Repetition issues
5. Weak sections that need improvement

RULES:
- Return ONLY valid JSON — no markdown, no explanations, no code fences.
- Be strict and realistic — do not inflate scores.

REQUIRED OUTPUT FORMAT:
{{
    "resume_quality_score": integer 0-100,
    "weak_sections": [
        {{"section_name": "...", "issue": "...", "recommendation": "..."}}
    ],
    "recommendations": ["..."],
    "optimization_priority": ["..."]
}}

RESUME:
{resume}
"""

ATS_SCORING_PROMPT = """You are an expert ATS scoring engine. Score this resume against the job description.

TASK: Return ONLY valid JSON matching the schema below. Do not include markdown, notes, or explanation outside of JSON.

OUTPUT SCHEMA:
{
    "keyword_score": integer 0-100,
    "experience_score": integer 0-100,
    "section_score": integer 0-100,
    "format_score": integer 0-100,
    "impact_score": integer 0-100,
    "overall_score": integer 0-100,
    "matched_keywords": ["..."],
    "missing_keywords": ["..."],
    "weak_sections": [
        {"section_name": "...", "issue": "...", "recommendation": "..."}
    ],
    "recommendations": ["..."],
    "optimization_priority": ["..."],
    "score_reasoning": "..."
}

SCORING WEIGHTS:
- keyword_score * 0.35
- experience_score * 0.25
- section_score * 0.20
- format_score * 0.10
- impact_score * 0.10

GITHUB PROJECTS:
{github_projects}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume}
"""