# prompts.py

def resume_enhance_prompt(resume_text: str, job_role: str) -> str:
    """
    Builds a detailed prompt for the LLM to enhance the resume.
    """
    return f"""
You are an expert resume writer and ATS (Applicant Tracking System) specialist.

User's target job role: {job_role}

Here is the user's current resume content:
\"\"\" 
{resume_text}
\"\"\"

Your tasks:

1. Rewrite the resume bullet points to be:
   - Action-oriented and impact-driven
   - Clear, concise, and professional
   - Relevant to the job role: {job_role}
   - Quantified where possible (e.g., "improved X by 20%")

2. Create a 3–4 line professional summary tailored to {job_role}.

3. Suggest 8–12 key skills (mix of technical and soft skills) that should appear in the resume for {job_role}.

Return the answer in this exact structure (no extra text):

SUMMARY:
- line 1
- line 2
- line 3

IMPROVED BULLETS:
- bullet 1
- bullet 2
- bullet 3
...

SUGGESTED SKILLS:
- skill 1
- skill 2
- skill 3
...
"""
