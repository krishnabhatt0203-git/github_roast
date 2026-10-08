from flask import Flask, render_template, request

from utils.github_api import (
    get_github_profile,
    get_repositories
)

from utils.ai_analyzer import analyze_profile


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        # Check username
        if not username:
            return render_template(
                "index.html",
                error="Please enter a GitHub username."
            )

        try:
            # --------------------------------
            # STEP 1: Get GitHub Profile
            # --------------------------------
            profile, error = get_github_profile(username)

            if error:
                return render_template(
                    "index.html",
                    error=error
                )

            # --------------------------------
            # STEP 2: Get GitHub Repositories
            # --------------------------------
            repos = get_repositories(username)

            # Add repositories inside profile
            # This also supports result.html templates
            # that use profile.repositories
            profile["repositories"] = repos

            # --------------------------------
            # STEP 3: AI Analysis
            # --------------------------------
            ai_result = analyze_profile(
                profile,
                repos
            )

            # --------------------------------
            # STEP 4: Show Result Page
            # --------------------------------
            return render_template(
                "result.html",
                profile=profile,
                repos=repos,
                analysis=ai_result
            )

        except Exception as e:

            print("ERROR:", e)

            return render_template(
                "index.html",
                error=f"Something went wrong: {str(e)}"
            )

    # --------------------------------
    # GET request
    # --------------------------------
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)