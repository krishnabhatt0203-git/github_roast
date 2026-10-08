import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API = "https://api.github.com"


def get_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    token = os.getenv("GITHUB_TOKEN", "").strip()

    # Don't send placeholder token
    if token and token not in [
        "your_github_token_here",
        "your_token_here"
    ]:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def get_github_profile(username):

    username = username.strip()

    if not username:
        return None, "Please enter a GitHub username."

    url = f"{GITHUB_API}/users/{username}"

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            timeout=10
        )

        if response.status_code == 404:
            return None, f"User '{username}' was not found on GitHub."

        if response.status_code == 401:
            return None, "GitHub token is invalid. Check your GITHUB_TOKEN."

        if response.status_code == 403:
            return None, (
                "GitHub API rate limit reached. "
                "Try again later or add a valid GitHub token."
            )

        if response.status_code != 200:
            return None, (
                f"GitHub API error: HTTP {response.status_code}"
            )

        return response.json(), None

    except requests.exceptions.RequestException as e:
        return None, f"Could not connect to GitHub: {str(e)}"


def get_repositories(username):

    url = f"{GITHUB_API}/users/{username}/repos"

    params = {
        "sort": "updated",
        "direction": "desc",
        "per_page": 100
    }

    try:
        response = requests.get(
            url,
            headers=get_headers(),
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        return response.json()

    except requests.exceptions.RequestException:
        return []


def get_profile_and_repos(username):

    profile, error = get_github_profile(username)

    if error:
        return None, None, error

    repos = get_repositories(username)

    return profile, repos, None