from github_graphql import get_viewer_login
from github_graphql import fetch_comments_of_issue
from dotenv import load_dotenv
import os
from github_graphql import get_all_issues
import json

# Load environment variables from the .env file
load_dotenv()


# Access the token value
personal_access_token = os.getenv("TOKEN_SECRET")
BOARD_URL = os.getenv("BOARD_URL")
owner = os.getenv("owner")
repo_name = os.getenv("repo_name")
login = os.getenv("login")
desired_states = os.getenv("DESIRED_STATES")

issue_id = os.getenv("issue_id")
new_assignee_id = os.getenv("new_assignee_id")
new_assignee_id = os.getenv("updated_assignee")
new_milestone_id = os.getenv("new_milestone_id")
label_ids = os.getenv("label_ids")


# Read the desired conditions for filtering from environment variables
desired_conditions = os.getenv("DESIRED_CONDITIONS")

# # Construct the conditions string
# conditions_str = ", ".join(desired_conditions)

viewer_login = get_viewer_login(personal_access_token)
print(f"Authenticated as: {viewer_login}")


issue_id = os.getenv("issue_id")
assignee = os.getenv("assignee")
new_assignee_id = os.getenv("new_assignee_id")
milestone = os.getenv("milestone")
labels = os.getenv("labels")


# Define your GitHub personal access token
token = os.getenv("TOKEN_SECRET")
owner = os.getenv("OWNER")
name = os.getenv("REPO_NAME")
issue_number = os.getenv("ISSUE_NUMBER")

fetch_comments_of_issue(token, issue_number, owner, name)

# Retrieve all issues and return as JSON
all_issues = get_all_issues(owner, name, token)
json_data = json.dumps(all_issues, indent=4)
print(json_data)
