
## How ATS systems actually work (recruiter perspective)

98% of Fortune 500 companies use ATS to screen resumes before any human sees them, and about 75% of resumes are rejected automatically. Here's the full picture of what's happening under the hood:

### The 6-layer pipeline

**Layer 1 — Parsing.** The ATS begins by parsing the resume's content — extracting text, headings, bullet points, contact information, and structured data such as education and work history. Poor formatting or unconventional layouts result in lost or misread information, negatively affecting the score.

**Layer 2 — JD Analysis.** The system also decomposes the job description into must-haves, preferred skills, and hard knockout criteria (location, authorization, visa status). A "no" on a knockout = auto-reject, regardless of score.

**Layer 3 — Weighted scoring.** ATS systems rely on weighted criteria: Keyword Relevance (30–40%) is the most critical factor — the system scans for job-specific terms like hard skills, certifications, and role-specific keywords. Formatting Compatibility (25–35%) ensures the ATS can parse your resume into structured data. Section Completeness (20–30%) checks that standard headings like "Experience", "Education", and "Skills" are present.

**Layer 4 — Matching technique.** Techniques such as TF-IDF and cosine similarity are used for matching. An ATS compatibility score is computed on a standardized scale, and the system identifies matched skills between the resume and job requirements.

**Layer 5 — Ranking.** Each keyword match contributes to an overall compatibility score, typically on a scale of 1–100. Only resumes scoring above a predetermined threshold (usually 60–80%) advance to human review.

**Layer 6 — Human recruiter.** They look at things ATS misses: career trajectory, writing quality, quantified achievements, and cultural fit signals.

---

## The 3 matching techniques (from basic to state-of-the-art)

A modern ATS pipeline has two parallel tracks: keyword match using set theory (intersection, difference, percentage calc) and semantic analysis using TF-IDF weighting + cosine similarity for contextual relevance.

The evolution is:
1. **Exact keyword match** — fast but brittle. "PM" doesn't match "Project Manager".
2. **TF-IDF + cosine similarity** — vectorizes both documents, compares them mathematically. The TF-IDF + cosine similarity combination demonstrates the best balance between speed and interpretability.
3. **Semantic / LLM** — embedding-based models such as word2vec and BERT outperform TF-IDF because they understand context and semantics, enabling more accurate candidate evaluation.

---

## Can you build this with just LLM + prompts?

**Yes, completely.** You don't need to train ML models or implement TF-IDF from scratch. Here's how each stage maps to prompts:

| Stage | What you prompt Gemini to do |
|---|---|
| Parse resume | Extract structured JSON: `{name, skills[], experience[], education[], certifications[]}` |
| Analyze JD | Extract: `{required_skills[], preferred_skills[], seniority, knockout_criteria[]}` |
| Score | Given parsed resume + JD JSON, return a score per category + overall 0–100 |
| Gap analysis | Return `{missing_keywords[], weak_sections[], suggestions[]}` |
| Suggestions | For each gap, return specific rewrite suggestions |

The key is to chain these as separate prompts (or one big structured prompt), always requesting JSON output so you can render it programmatically.

---

## Practical architecture for platform

```
User uploads resume (PDF/DOCX)
        ↓
Extract text (pdf-parse / mammoth.js)
        ↓
Send to Gemini: "Parse this resume into structured JSON"
        ↓
User pastes JD → Send to Gemini: "Parse this JD into requirements JSON"
        ↓
Send both to Gemini: "Score this resume against this JD, return {
  overall_score, keyword_score, format_score, 
  section_score, missing_keywords[], suggestions[]
}"
        ↓
Render score dashboard + actionable fix list
```

**Gemini advantages for this:** Gemini 1.5 Pro has a 1M token context window, so it can handle long resumes + JDs + company context all in one call. It also natively understands synonyms and semantics, so "led a team" matches "people management" without you building any NLP pipeline.

The only thing Gemini alone can't do is OCR on scanned image-PDFs — for that you'd use Google Document AI or pdf2image → Gemini Vision first.