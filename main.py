from github_graphql import get_viewer_login
from github_graphql import fetch_cards
from github_graphql import fetch_issues
from github_graphql import update_metadata
from github_graphql import fetch_issue_comments
from github_graphql import add_comment
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

import os

# Access the token value
personal_access_token = os.getenv("TOKEN_SECRET")
BOARD_URL = os.getenv("BOARD_URL")
owner = os.getenv("owner")
repo_name = os.getenv("repo_name")
login = os.getenv("login")
desired_states = os.getenv("DESIRED_STATES")

issue_number = os.getenv("issue_number")
updated_assignee = os.getenv("updated_assignee")
updated_milestone = os.getenv("updated_milestone")
updated_labels = os.getenv("updated_labels").split(",")
metadata_list = os.getenv("metadata_list").split(",")


# Read the desired conditions for filtering from environment variables
desired_conditions = os.getenv("DESIRED_CONDITIONS").split(",")

# Construct the conditions string
conditions_str = ", ".join(desired_conditions)

viewer_login = get_viewer_login(personal_access_token)
print(f"Authenticated as: {viewer_login}")

cards = fetch_cards(personal_access_token, BOARD_URL, owner, repo_name)
print("cards", cards)

issues = fetch_issues(
    personal_access_token, BOARD_URL, login, repo_name, desired_states, conditions_str
)
print("issues", issues)

issue_number = os.getenv("issue_number")

new_comment_body = os.getenv("new_comment_body")
update_metadata(
    personal_access_token,
    BOARD_URL,
    login,
    repo_name,
    issue_number,
    updated_assignee,
    updated_milestone,
    updated_labels,
    metadata_list,
)

# Fetch issue comments and print as JSON
comments_json = fetch_issue_comments(
    personal_access_token, BOARD_URL, login, repo_name, issue_number
)
print("Issue comments:")
print(comments_json)
assert len(comments_json) > 0
print("Fetch issue comments test passed.")

# Add a new comment to the issue
add_comment(personal_access_token, issue_number, new_comment_body)
