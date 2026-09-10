# ==========================================
# SKILL EXTRACTOR
# ==========================================


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

import re


def extract_skills(text):

    """
    Extract skills from resume text.
    """

    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:

        skill_lower = skill.lower()

        # Check for the complete skill
        pattern = r"(?<!\w)" + re.escape(skill_lower) + r"(?!\w)"

        if re.search(pattern, text_lower):

            found_skills.append(skill)

    return found_skills



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