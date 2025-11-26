# app.py

import datetime
import re
import streamlit as st

from prompts import resume_enhance_prompt
from llm_client import call_llm
from utils import clean_text
from parser import parse_llm_response

# ----------------- JD MATCH HELPERS -----------------

STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this", "your", "you",
    "our", "are", "will", "have", "has", "any", "all", "but", "about",
    "such", "into", "also", "able", "work", "working", "role", "job",
    "responsibilities", "requirements", "skills", "required", "years",
    "experience", "using", "knowledge", "good", "strong", "etc", "per",
    "week", "month", "year", "must", "should", "can", "ability"
}

def extract_keywords(text: str):
    """
    Extract simple keywords from text:
    - Lowercase
    - Only alphabetic tokens
    - Remove stopwords
    - Remove very short words
    Returns a set of keywords.
    """
    if not text:
        return set()

    text = text.lower()
    # Find words (letters only)
    words = re.findall(r"[a-zA-Z]+", text)
    keywords = {
        w for w in words
        if len(w) > 3 and w not in STOPWORDS
    }
    return keywords

def compute_jd_match(jd_text: str, resume_text: str):
    """
    Compute a simple JD vs Resume match score based on keyword overlap.
    Returns (score_percent, matched_keywords, missing_keywords).
    """
    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)

    if not jd_keywords:
        return 0, set(), set()

    matched = jd_keywords & resume_keywords
    missing = jd_keywords - resume_keywords

    score = round(len(matched) / len(jd_keywords) * 100)
    return score, matched, missing

# ----------------- DOWNLOAD + BULLET HELPERS -----------------

def build_download_payload(parsed, raw_text) -> str:
    """Create a nice text file with structured sections + raw output, safely handling None values."""
    def safe(x):
        return "" if x is None else str(x)

    combined = []

    combined.append("SUMMARY:")
    for line in parsed.get("summary", []):
        combined.append(f"- {safe(line)}")
    combined.append("")

    combined.append("IMPROVED BULLETS:")
    for b in parsed.get("bullets", []):
        combined.append(f"- {safe(b)}")
    combined.append("")

    combined.append("SUGGESTED SKILLS:")
    for s in parsed.get("skills", []):
        combined.append(f"- {safe(s)}")
    combined.append("")

    combined.append("RAW AI OUTPUT:")
    combined.append(safe(raw_text))

    return "\n".join(combined)


def extract_original_bullets(resume_text: str):
    """
    Very simple heuristic to extract 'original' bullet-style lines
    from the resume text for before-vs-after comparison.
    """
    bullets = []
    for line in resume_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        # Lines that start with typical bullet characters
        if stripped.startswith(("-", "•", "*")):
            # remove leading bullet chars
            while stripped and stripped[0] in "-•* ":
                stripped = stripped[1:]
            stripped = stripped.strip()
            if len(stripped) > 10:
                bullets.append(stripped)
            continue

        # As a fallback, treat reasonably long lines as bullet-like
        if len(stripped) > 40:  # arbitrary length threshold
            bullets.append(stripped)

    return bullets

# ----------------- MAIN APP -----------------

def main():
    st.set_page_config(
        page_title="AI Resume Enhancer",
        page_icon="🧠",
        layout="wide",
    )

    st.title("🧠 AI Resume Enhancer")
    st.caption("Generate ATS-friendly, impact-driven resume content and check JD match using a Generative AI model.")

    # ---- LEFT PANEL: INPUTS ----
    left, right = st.columns([2, 3])

    with left:
        st.markdown("### ✍️ Input")

        job_role = st.text_input(
            "🎯 Target Job Role",
            placeholder="e.g. Data Analyst, Business Analyst, Marketing Executive",
        )

        resume_text = st.text_area(
            "📄 Paste your current resume text",
            height=260,
            placeholder=(
                "Copy-paste your resume content (education, projects, experience, internships, skills)..."
            ),
        )

        jd_text = st.text_area(
            "📌 Optional: Job Description (JD)",
            height=160,
            placeholder="Paste JD here if you want the AI and JD Match Score to tailor content to a specific role/company.",
        )

        enhance_button = st.button("✨ Enhance My Resume", use_container_width=True)

        st.info(
            "Tip: Start with one role (e.g. Data Analyst). "
            "You can run again for other roles like Business Analyst or Marketing Executive."
        )

    # ---- RIGHT PANEL: OUTPUT ----
    with right:
        st.markdown("### ✅ AI-Optimized Output")

        if not enhance_button:
            st.write("Fill the details on the left and click **Enhance My Resume**.")
        else:
            job_role_clean = clean_text(job_role)
            resume_text_clean = clean_text(resume_text)
            jd_text_clean = clean_text(jd_text)

            if not job_role_clean or not resume_text_clean:
                st.warning("Please enter both a target job role **and** your resume text.")
                return

            # Build prompt (also include JD if provided)
            prompt = resume_enhance_prompt(resume_text_clean, job_role_clean)
            if jd_text_clean:
                prompt += f"""

Also consider the following Job Description when tailoring the content:

\"\"\"{jd_text_clean}\"\"\"
"""

            with st.spinner("🔄 Talking to the AI model and optimizing your resume..."):
                ai_response = call_llm(prompt)

            # If llm_client returned an error string, show it clearly
            if isinstance(ai_response, str) and ai_response.startswith("❌ Error"):
                st.error(ai_response)
                return

            # Parse structured sections from AI output
            parsed = parse_llm_response(ai_response)
            original_bullets = extract_original_bullets(resume_text_clean)

            # Precompute JD match (local, no AI)
            jd_score, jd_matched, jd_missing = compute_jd_match(jd_text_clean, resume_text_clean) if jd_text_clean else (0, set(), set())

            # Use tabs for a clean UX
            tab_summary, tab_bullets, tab_skills, tab_compare, tab_jd, tab_raw = st.tabs(
                ["📝 Summary", "📌 Bullet Points", "🧩 Skills", "🔄 Before vs After", "🎯 JD Match", "🧾 Full Output"]
            )

            # --- SUMMARY TAB ---
            with tab_summary:
                st.subheader("Professional Summary")

                if parsed["summary"]:
                    with st.container():
                        st.markdown(
                            """
<div style="padding: 12px; border-radius: 8px; border: 1px solid #e0e0e0; background-color: #fafafa;">
""",
                            unsafe_allow_html=True,
                        )
                        for line in parsed["summary"]:
                            st.markdown(f"- {line}")
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("No structured summary detected. Check the **Full Output** tab.")

            # --- BULLETS TAB ---
            with tab_bullets:
                st.subheader("Improved Bullet Points")
                if parsed["bullets"]:
                    for b in parsed["bullets"]:
                        st.markdown(f"✅ {b}")
                else:
                    st.info("No structured bullet points detected. Check the **Full Output** tab.")

            # --- SKILLS TAB ---
            with tab_skills:
                st.subheader("Suggested Skills (Add to Skills section)")

                if parsed["skills"]:
                    cols = st.columns(4)
                    for i, skill in enumerate(parsed["skills"]):
                        cols[i % 4].markdown(
                            f"""
<div style="display:inline-block; padding:4px 10px; margin:4px 0; border-radius:16px; border:1px solid #ddd; font-size:0.9rem;">
{skill}
</div>
""",
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No structured skills detected. Check the **Full Output** tab.")

            # --- BEFORE vs AFTER TAB ---
            with tab_compare:
                st.subheader("Before vs After (Original vs AI-Improved)")

                if not original_bullets and not parsed["bullets"]:
                    st.info("No clear bullet points detected. Try formatting your resume bullets as lines starting with - or •.")
                else:
                    col_before, col_after = st.columns(2)
                    col_before.markdown("**🟥 Original Bullet Points**")
                    col_after.markdown("**🟩 AI-Improved Bullet Points**")

                    max_len = max(len(original_bullets), len(parsed["bullets"]))
                    if max_len == 0:
                        st.info("Nothing to compare yet.")
                    else:
                        for i in range(max_len):
                            orig = original_bullets[i] if i < len(original_bullets) else ""
                            new = parsed["bullets"][i] if i < len(parsed["bullets"]) else ""

                            with col_before:
                                st.markdown(f"- {orig}" if orig else "- _[no original bullet]_")
                            with col_after:
                                st.markdown(f"- {new}" if new else "- _[no improved bullet]_")

                        st.caption(
                            "Note: Matching is position-based and approximate. You can manually reorder or edit bullets in your resume."
                        )

            # --- JD MATCH TAB ---
            with tab_jd:
                st.subheader("🎯 JD Match Score")

                if not jd_text_clean:
                    st.info("Paste a Job Description (JD) on the left to calculate a JD match score.")
                else:
                    st.metric("Match Score (approx)", f"{jd_score} %")

                    st.markdown("#### ✅ Keywords matched (already in your resume)")
                    if jd_matched:
                        cols_match = st.columns(4)
                        for i, kw in enumerate(sorted(jd_matched)):
                            cols_match[i % 4].markdown(
                                f"""
<div style="display:inline-block; padding:4px 10px; margin:4px 0; border-radius:16px; border:1px solid #c8e6c9; background-color:#f1f8e9; font-size:0.9rem;">
{kw}
</div>
""",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.write("_No significant JD keywords found in your resume yet._")

                    st.markdown("#### ❌ Important JD keywords missing (consider adding if true for you)")
                    if jd_missing:
                        cols_miss = st.columns(4)
                        for i, kw in enumerate(sorted(jd_missing)):
                            cols_miss[i % 4].markdown(
                                f"""
<div style="display:inline-block; padding:4px 10px; margin:4px 0; border-radius:16px; border:1px solid #ffcdd2; background-color:#ffebee; font-size:0.9rem;">
{kw}
</div>
""",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.write("_Great! Your resume already covers most of the JD keywords._")

                    st.caption(
                        "Note: This is a simple keyword-based score. It does not fully capture context, but it helps identify missing terminology."
                    )

            # --- RAW OUTPUT TAB ---
            with tab_raw:
                st.subheader("Raw AI Output (for debugging or manual copy)")
                st.text_area(
                    "Complete AI Response",
                    value=ai_response,
                    height=260,
                )

            # ---- Download Button (applies to all tabs) ----
            st.markdown("---")
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"resume_enhanced_{job_role_clean.replace(' ', '_')}_{now}.txt"
            payload = build_download_payload(parsed, ai_response)

            st.download_button(
                label="📥 Download All as .txt",
                data=payload,
                file_name=filename,
                mime="text/plain",
            )

    st.markdown("---")
    st.caption("Built by Yash Sharma · Gen AI Resume Project")


if __name__ == "__main__":
    main()
