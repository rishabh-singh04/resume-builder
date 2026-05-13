"""Job Description parser prompt."""

JD_PARSER_PROMPT = """You are an expert technical recruiter and ATS specialist.

TASK: Parse the job description below into structured JSON.

RULES:
- Return ONLY valid JSON — no markdown, no explanations, no code fences.
- Deduplicate keywords.
- Normalize technology names (e.g. "JS" → "JavaScript", "Postgres" → "PostgreSQL").
- Infer seniority from years of experience: 0–1 → Junior, 2–4 → Mid-Level, 5–8 → Senior, 8+ → Lead.
- Identify hidden expectations (unstated but implied requirements).
- Keep all extracted content factual.

REQUIRED FIELDS:
- role_title: string
- company_name: string or null
- seniority: one of [Intern, Junior, Mid-Level, Senior, Staff, Lead, Principal] or null
- employment_type: one of [Full-Time, Part-Time, Contract, Internship, Freelance] or null
- location: string or null
- remote_allowed: boolean
- required_skills: list of strings
- preferred_skills: list of strings
- tech_stack: list of strings
- responsibilities: list of strings
- qualifications: list of strings
- ats_keywords: list of strings (all important terms for ATS matching)
- soft_skills: list of strings
- hidden_expectations: list of strings
- raw_text: the original JD text verbatim

JOB DESCRIPTION:
{jd_text}"""