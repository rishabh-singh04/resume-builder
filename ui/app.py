"""
Resume Agent — Streamlit UI.

Run with:
    streamlit run ui/app.py
"""

import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
from loguru import logger

from services.orchestrator import ResumeOrchestrator, PipelineResult
import asyncio
import tempfile


# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Resume Agent — AI Resume Builder",
    page_icon="📄",
    layout="wide",
)


# ─────────────────────────────────────────────
# Cached Orchestrator
# ─────────────────────────────────────────────


@st.cache_resource
def get_orchestrator():
    return ResumeOrchestrator()


# ─────────────────────────────────────────────
# UI Layout
# ─────────────────────────────────────────────

st.title("📄 Resume Agent")
st.markdown("*AI-powered tailored resume builder with ATS optimization*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    github_username = st.text_input("GitHub Username", placeholder="e.g. octocat")
    st.divider()
    st.markdown("**How it works:**")
    st.markdown(
        "1. Paste a Job Description\n"
        "2. Upload your resume (PDF) or paste text\n"
        "3. Click Generate\n"
        "4. Download your tailored resume"
    )

# Main area — two columns
col_jd, col_resume = st.columns(2)

with col_jd:
    st.subheader("📋 Job Description")
    jd_text = st.text_area(
        "Paste the full job description",
        height=300,
        placeholder="Paste the complete job description here...",
    )

with col_resume:
    st.subheader("📄 Your Resume")
    input_method = st.radio("Input method:", ["Upload PDF", "Paste Text"], horizontal=True)

    resume_text = None
    resume_file = None

    if input_method == "Upload PDF":
        resume_file = st.file_uploader("Upload resume PDF", type=["pdf"])
    else:
        resume_text = st.text_area(
            "Paste your resume text",
            height=250,
            placeholder="Paste your resume content here...",
        )

# Generate button
st.divider()

if st.button("🚀 Generate Tailored Resume", type="primary", use_container_width=True):
    if not jd_text:
        st.error("Please provide a job description.")
    elif not resume_file and not resume_text:
        st.error("Please provide your resume (PDF or text).")
    else:
        orchestrator = get_orchestrator()

        with st.status("🔄 Generating tailored resume...", expanded=True) as status:
            try:
                # Handle PDF upload
                pdf_path = None
                if resume_file:
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        tmp.write(resume_file.read())
                        pdf_path = tmp.name

                st.write("📋 Parsing job description...")
                st.write("📄 Parsing resume...")

                # Run pipeline
                result: PipelineResult = asyncio.run(
                    orchestrator.run_pipeline(
                        jd_text=jd_text,
                        resume_pdf_path=pdf_path,
                        resume_text=resume_text,
                        github_username=github_username or None,
                    )
                )

                status.update(label="✅ Resume generated!", state="complete")

                # Clean up temp file
                if pdf_path:
                    Path(pdf_path).unlink(missing_ok=True)

            except Exception as e:
                status.update(label="❌ Generation failed", state="error")
                st.error(f"Error: {str(e)}")
                logger.exception("Pipeline failed in UI")
                st.stop()

        # ─── Results ─────────────────────────────────
        st.divider()
        st.header("📊 Results")

        # ATS Score
        score = result.ats_report.ats_score
        col_score, col_meta = st.columns([1, 2])

        with col_score:
            color = "green" if score >= 85 else "orange" if score >= 70 else "red"
            st.metric("ATS Score", f"{score}/100")

        with col_meta:
            st.markdown(f"**Target Role:** {result.tailored_resume.target_role or 'N/A'}")
            st.markdown(f"**Company:** {result.tailored_resume.target_company or 'N/A'}")

        # Tabs for detailed results
        tab_resume, tab_ats, tab_changes = st.tabs(
            ["📄 Tailored Resume", "📊 ATS Report", "📝 Changes"]
        )

        with tab_resume:
            if result.tailored_resume.professional_summary:
                st.subheader("Summary")
                st.write(result.tailored_resume.professional_summary)

            if result.tailored_resume.optimized_work_experience:
                st.subheader("Experience")
                for exp in result.tailored_resume.optimized_work_experience:
                    st.markdown(f"**{exp.role}** at {exp.company}")
                    for bullet in exp.bullet_points:
                        st.markdown(f"- {bullet}")

            if result.tailored_resume.optimized_projects:
                st.subheader("Projects")
                for proj in result.tailored_resume.optimized_projects:
                    st.markdown(
                        f"**{proj.project_name}** | {', '.join(proj.technologies_used)}"
                    )
                    for bullet in proj.bullet_points:
                        st.markdown(f"- {bullet}")

        with tab_ats:
            st.json(result.ats_report.model_dump())

        with tab_changes:
            if result.tailored_resume.optimized_bullets:
                for change in result.tailored_resume.optimized_bullets:
                    st.markdown("**Original:**")
                    st.text(change.original)
                    st.markdown("**Optimized:**")
                    st.text(change.optimized)
                    st.divider()
            else:
                st.info("No bullet point changes tracked.")

        # Downloads
        st.divider()
        st.subheader("📥 Downloads")

        col_dl1, col_dl2, col_dl3 = st.columns(3)

        with col_dl1:
            st.download_button(
                "📄 Download Resume JSON",
                data=result.tailored_resume.model_dump_json(indent=2),
                file_name="tailored_resume.json",
                mime="application/json",
            )

        with col_dl2:
            st.download_button(
                "📊 Download ATS Report",
                data=result.ats_report.model_dump_json(indent=2),
                file_name="ats_report.json",
                mime="application/json",
            )

        with col_dl3:
            if result.tex_path and Path(result.tex_path).exists():
                with open(result.tex_path, "r") as f:
                    tex_content = f.read()
                st.download_button(
                    "📝 Download .tex File",
                    data=tex_content,
                    file_name="resume.tex",
                    mime="text/plain",
                )
