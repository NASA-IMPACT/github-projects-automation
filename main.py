from github_graphql import get_viewer_login
from github_graphql import fetch_comments_of_issue_and_update
from dotenv import load_dotenv
import os
from github_graphql import get_all_issues
import json
from github_graphql import get_all_issues_details
from github_graphql import get_PR_Metrics
from github_graphql import issue_management_metrics_calculation
from github_graphql import project_activity_metrics_calculation
from github_graphql import contributor_activity_metrics_calculation
from github_graphql import add_metadata_to_project_board
from github_graphql import add_metrics_from_one_board_to_another_board
import secrets
from flask import Flask, request
from github import Github
import hmac
import hashlib
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request

# from github import Github
import hmac
import hashlib
import requests

from flask import Flask, request, jsonify
import hmac
import hashlib


# from github_graphql import filter_cards_states_estimate_metadata

# from github_graphql import update_issue_details

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

fetch_comments_of_issue_and_update(token, issue_number, owner, name)

# Retrieve all issues and return as JSON
all_issues = get_all_issues(owner, name, token)
json_data = json.dumps(all_issues, indent=4)
print(json_data)

issue_state = os.getenv("ISSUE_STATE")
estimate = os.getenv("ESTIMATE")
metadata = os.getenv("METADATA")
project_id = os.getenv("project_id")

destination_owner = os.getenv("destination_owner")
destination_name = os.getenv("destination_name")
# to retrieve open and closed issues, assignees, and completion time
get_all_issues_details(owner, name, token)

# to fetch PR data with limited comments per PR
get_PR_Metrics(owner, name, token)


issue_management_metrics_calculation(owner, name, token)
project_activity_metrics_calculation(owner, name, token)
contributor_activity_metrics_calculation(owner, name, token)
add_metadata_to_project_board(owner, name, token, project_id)


add_metrics_from_one_board_to_another_board(
    owner, name, token, destination_owner, destination_name
)


app = Flask(__name__)
github_access_token = token


app = Flask(__name__)
secret_key = os.getenv("secret_key").encode()
github_access_token = token
slack_token = os.getenv("slack_token")
slack_channel = os.getenv("slack_channel")


@app.route("/", methods=["GET"])
def ping():
    return "testing to determine if the hook is successfully created."


def send_slack_message(message):
    client = WebClient(token=slack_token)
    response = client.chat_postMessage(channel=slack_channel, text=message)
    if response["ok"]:
        print(f"Slack message sent: {response['message']['text']}")
    else:
        print(f"Failed to send Slack message: {response['error']}")


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        signature = request.headers.get("X-Hub-Signature-256")
        if signature is None:
            return "Signature missing", 400

        digest = hmac.new(
            secret_key, msg=request.data, digestmod=hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest("sha256=" + digest, signature):
            return "Invalid signature", 401

        payload = request.get_json()
        print("payload", payload)
        if "project_card" in payload:
            project_name = payload["project_card"]["project"]["name"]
            card_title = payload["project_card"]["note"]
            column = payload["project_card"]["column_name"]

            if payload.get("action") == "created":
                print(f'New card "{card_title}" created in "{project_name}" project.')
            elif payload.get("action") == "moved":
                print(
                    f'Card "{card_title}" moved to "{column}" column in "{project_name}" project.'
                )
            elif payload.get("action") == "deleted":
                print(f'Card "{card_title}" deleted from "{project_name}" project.')
            else:
                print("Unknown action for project_card event.")

        return "Webhook received", 200

    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return "Error processing webhook", 500


@app.route("/", methods=["GET"])
def root():
    return "Hello, World!"


send_slack_message("Message delivered successfully.")


# @app.route("/", methods=["GET"])
# def root():
#     return "Hello, World!"


if __name__ == "__main__":
    app.run(port=5000)
