# ==========================================
# SKILL EXTRACTOR
# ==========================================

import json
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


# List of skills that the application can detect

SKILLS = [

    # -------------------------------
    # Programming Languages
    # -------------------------------

    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "Go",
    "Ruby",
    "PHP",
    "Kotlin",
    "Swift",


    # -------------------------------
    # Web Development
    # -------------------------------

    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue",
    "Node.js",
    "Django",
    "Flask",
    "FastAPI",
    "Spring Boot",


    # -------------------------------
    # Databases
    # -------------------------------

    "SQL",
    "SQLC",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Oracle",
    "Redis",


    # -------------------------------
    # Cloud Technologies
    # -------------------------------

    "AWS",
    "Azure",
    "Microsoft Azure",
    "Google Cloud",
    "GCP",


    # -------------------------------
    # DevOps
    # -------------------------------

    "Docker",
    "Kubernetes",
    "Jenkins",
    "Git",
    "GitHub",
    "GitLab",


    # -------------------------------
    # Data Science / AI
    # -------------------------------

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Pandas",
    "NumPy",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",


    # -------------------------------
    # Salesforce
    # -------------------------------

    "Salesforce",
    "Apex",
    "SOQL",
    "LWC",
    "Visualforce"
]

# ==========================================
# SKILL CATEGORIES
# ==========================================

SKILL_CATEGORIES = {

    "Programming Languages": [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "C",
        "C++",
        "C#",
        "Go",
        "Ruby",
        "PHP",
        "Kotlin",
        "Swift"
    ],

    "Web Development": [
        "HTML",
        "CSS",
        "React",
        "Angular",
        "Vue",
        "Node.js",
        "Express.js",
        "Django",
        "Flask",
        "FastAPI",
        "Spring Boot"
    ],

    "Databases": [
        "SQL",
        "SQLC",
        "MySQL",
        "Supabase",
        "PostgreSQL",
        "MongoDB",
        "Oracle",
        "Redis"
    ],

    "Cloud Technologies": [
        "AWS",
        "Azure",
        "Microsoft Azure",
        "Google Cloud",
        "GCP"
    ],

    "DevOps": [
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Git",
        "GitHub",
        "GitLab",
        "NGINX",
        "GitHub Actions",
        "Linux",
        "CI/CD",
        "Docker Compose",
    ],

    "Data Science / AI": [
        "Machine Learning",
        "Deep Learning",
        "Artificial Intelligence",
        "Data Science",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Gemini API",
        "Pinecone",
        "RAG",
        "MiniLM",
    ],

    "Salesforce": [
        "Salesforce",
        "Apex",
        "SOQL",
        "LWC",
        "Visualforce"
    ]
}

# ==========================================
# FUNCTION TO EXTRACT SKILLS
# ==========================================

SUPPORTED_SKILLS = list(dict.fromkeys(
    skill
    for category_skills in SKILL_CATEGORIES.values()
    for skill in category_skills
))

SKILL_ALIASES = {
    "pyton": "Python",
    "pythone": "Python",
    "python 3": "Python",
    "golang": "Go",
    "go lang": "Go",
    "sqlc": "SQLC",
}


def _canonicalize_skills(skills):

    canonical_skills = {
        skill.lower(): skill
        for skill in SUPPORTED_SKILLS
    }
    canonical_skills.update(
        {alias: skill for alias, skill in SKILL_ALIASES.items()}
    )

    return list(dict.fromkeys(
        canonical_skills[skill.strip().lower()]
        for skill in skills
        if isinstance(skill, str)
        and skill.strip().lower() in canonical_skills
    ))


def extract_skills(text):

    """
    Extract skills semantically with Gemini and normalize them to the app catalog.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Set it before extracting skills."
        )

    client = genai.Client(api_key=api_key)
    prompt = f"""
Identify the technical skills represented in the text below, including skills
described by equivalent wording rather than only exact mentions.

Return only skills from this canonical catalog, using the exact spelling shown:
{", ".join(SUPPORTED_SKILLS)}

Normalize common variants and typos, for example: "pyton" or "pythone" to
"Python", "golang" to "Go", and "sqlc" to "SQLC".

Text:
{text}
"""

    request_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "OBJECT",
            "properties": {
                "skills": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                }
            },
            "required": ["skills"],
        },
    )

    configured_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    models_to_try = list(dict.fromkeys([
        configured_model,
        os.getenv("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash"),
    ]))

    response = None
    last_error = None
    for model in models_to_try:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=request_config,
            )
            break
        except Exception as error:
            last_error = error

    if response is None:
        raise RuntimeError("Gemini skill extraction failed.") from last_error

    try:
        result = json.loads(response.text)
        return _canonicalize_skills(result.get("skills", []))
    except (TypeError, ValueError, AttributeError) as error:
        raise RuntimeError("Gemini returned an invalid skill response.") from error



# ==========================================
# FUNCTION TO CATEGORIZE SKILLS
# ==========================================

def categorize_skills(found_skills):

    categorized = {}

    for category, category_skills in SKILL_CATEGORIES.items():

        matching_skills = []

        for skill in found_skills:

            if skill in category_skills:

                matching_skills.append(skill)

        if matching_skills:

            categorized[category] = matching_skills

    return categorized


# ==========================================
# FUNCTION TO CALCULATE SKILL MATCH
# ==========================================

def calculate_skill_match(resume_skills, job_skills):

    resume_set = set(skill.lower() for skill in resume_skills)
    job_set = set(skill.lower() for skill in job_skills)

    if not job_set:
        return {
            "match_percentage": 0,
            "matched_skills": [],
            "missing_skills": job_skills
        }

    matched_lower = resume_set.intersection(job_set)
    missing_lower = job_set - resume_set

    matched_skills = [
        skill for skill in job_skills
        if skill.lower() in matched_lower
    ]

    missing_skills = [
        skill for skill in job_skills
        if skill.lower() in missing_lower
    ]

    match_percentage = (
        len(matched_skills) / len(job_skills)
    ) * 100

    return {
        "match_percentage": round(match_percentage, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }