import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


def analyze_profile(profile, repos):

    # If Gemini API key is not configured
    if not client:
        return fallback_analysis(profile, repos)

    repo_text = ""

    for repo in repos[:20]:
        repo_text += f"""
        Repository: {repo.get('name')}
        Description: {repo.get('description')}
        Stars: {repo.get('stargazers_count')}
        Forks: {repo.get('forks_count')}
        Language: {repo.get('language')}
        URL: {repo.get('html_url')}
        """

    prompt = f"""
You are an expert GitHub profile reviewer and career mentor.

Analyze this GitHub developer profile honestly but constructively.

PROFILE:
Username: {profile.get('login')}
Name: {profile.get('name')}
Bio: {profile.get('bio')}
Public Repositories: {profile.get('public_repos')}
Followers: {profile.get('followers')}
Following: {profile.get('following')}

REPOSITORIES:
{repo_text}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "profile_score": 0,
    "project_score": 0,
    "activity_score": 0,
    "documentation_score": 0,
    "roast": "",
    "strengths": [],
    "weaknesses": [],
    "recommendations": [],
    "career_advice": "",
    "priority": []
}}

Scoring:
- profile_score: 0-100
- project_score: 0-100
- activity_score: 0-100
- documentation_score: 0-100

Be honest.
Do not insult the person.
Give practical recommendations that a student/developer can actually implement.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown JSON fences if Gemini adds them
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        return json.loads(text)

    except Exception as e:
        print("Gemini analysis error:", e)
        return fallback_analysis(profile, repos)


def fallback_analysis(profile, repos):

    repo_count = profile.get("public_repos", 0)

    if repo_count >= 10:
        project_score = 85
    elif repo_count >= 5:
        project_score = 70
    elif repo_count >= 2:
        project_score = 55
    else:
        project_score = 30

    return {
        "profile_score": 60,
        "project_score": project_score,
        "activity_score": 50,
        "documentation_score": 40,

        "roast": (
            "Your GitHub has potential, but it needs more polish. "
            "Think of it as a portfolio that is still under construction."
        ),

        "strengths": [
            f"You have {repo_count} public repositories.",
            "Your GitHub profile can be improved into a strong developer portfolio."
        ],

        "weaknesses": [
            "Repository documentation needs improvement.",
            "Projects should have clear README files.",
            "Profile presentation can be stronger."
        ],

        "recommendations": [
            "Add a professional GitHub profile README.",
            "Add README files to important projects.",
            "Pin your best projects.",
            "Add screenshots and live demos.",
            "Keep projects organized and updated."
        ],

        "career_advice": (
            "Focus on building 3-5 strong projects rather than many incomplete projects. "
            "Make each project easy for recruiters to understand."
        ),

        "priority": [
            "Create a strong profile README",
            "Improve project documentation",
            "Pin your best projects",
            "Add live demos and screenshots"
        ]
    }