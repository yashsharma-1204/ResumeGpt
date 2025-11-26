# llm_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env variables into Python environment
load_dotenv()

# Read key + model from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")

if not OPENAI_API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY is missing in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def call_llm(prompt: str) -> str:
    return
    """
    SUMMARY:
- Enthusiastic entry-level data analyst with a strong foundation in statistics and Excel.
- Experienced in working with SQL, Power BI, and data visualization for academic projects.
- Passionate about deriving business insights from raw data and presenting them clearly.

IMPROVED BULLETS:
- Analyzed T20 World Cup dataset using SQL and Excel to uncover patterns in player and team performance.
- Developed interactive Power BI dashboards to track strike rate, economy, and win probability across matches.
- Cleaned and transformed raw cricket data, improving data quality and reliability for decision-making.
- Presented insights and recommendations to classmates using clear charts and storytelling.

SUGGESTED SKILLS:
- SQL
- Excel
- Power BI
- Data Visualization
- Exploratory Data Analysis (EDA)
- Python (Pandas, NumPy)
- Communication
- Problem-Solving
- Critical Thinking
- Attention to Detail
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        # Extract text from API response
        content = response.choices[0].message.content
        return content.strip()

    except Exception as e:
        return f"❌ Error communicating with the AI model:\n{e}"
