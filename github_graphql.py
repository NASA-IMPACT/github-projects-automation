import json
import requests
from enum import Enum
from dotenv import dotenv_values
import os
import pytest
from dotenv import load_dotenv


class IssueState(Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    # Add more states if needed


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def get_viewer_login(personal_access_token):
    graphql_query = """
        query ($status: [IssueState!]) {
            viewer {
                id
                login
                projectV2(number: 1) {
                    id
                    title
                    items(first: 100) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        nodes {
                            databaseId
                            id
                            content {
                                __typename
                                ... on Issue {
                                    url
                                }
                            }
                            fieldValues(first: 20) {
                                nodes {
                                    ... on ProjectV2ItemFieldSingleSelectValue {
                                        name
                                        id
                                    }
                                    ... on ProjectV2ItemFieldLabelValue {
                                        labels(first: 1) {
                                            nodes {
                                                id
                                                name
                                                issues(first: 20, states: $status, orderBy: { field: CREATED_AT, direction: DESC }) {
                                                    nodes {
                                                        url
                                                        title
                                                        createdAt
                                                        comments(first: 5) {
                                                            nodes {
                                                                author {
                                                                    login
                                                                }
                                                                bodyText
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    ... on ProjectV2ItemFieldTextValue {
                                        text
                                        id
                                        updatedAt
                                        creator {
                                            url
                                        }
                                    }
                                    ... on ProjectV2ItemFieldMilestoneValue {
                                        milestone {
                                            id
                                        }
                                    }
                                    ... on ProjectV2ItemFieldRepositoryValue {
                                        repository {
                                            id
                                            url
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    # Set the headers for the request
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }
    # Load environment variables from .env file
    env = dotenv_values(".env")

    status_filter = [
        IssueState.CLOSED
    ]  # Set the desired status filter here as a list of IssueState values

    # Load the status filter from the environment variable, if available
    env_status = env.get("STATUS")
    if env_status:
        try:
            status_filter = [
                IssueState(s.strip().upper()) for s in env_status.split(",")
            ]
        except ValueError:
            print("Invalid status value in .env file. Using default status filter.")

    variables = {
        "status": status_filter,
        # "estimate": env_estimate,
        # "metadata": env_metadata,
    }

    # variables = {"status": status_filter}

    # Set the GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Serialize the request payload manually with a custom encoder
    payload = json.dumps(
        {"query": graphql_query, "variables": variables}, cls=EnumEncoder
    )

    # Send the GraphQL request
    response = requests.post(url, data=payload, headers=headers)

    # Get the JSON response
    json_data = response.json()

    # Print the JSON data
    print("I am here", json_data)
    return json_data["data"]["viewer"]["login"]


def fetch_comments_of_issue(token, issue_number, owner, name):
    # Define the GraphQL query
    query = """
    query GetIssueComments {
    repository(owner: "%s", name: "%s") {
        issue(number: %s) {
        comments(first: 100) {
            edges {
            node {
                bodyText
                author {
                login
                }
            }
            }
        }
        }
    }
    }
    """ % (
        owner,
        name,
        issue_number,
    )
    # Send the GraphQL request to the GitHub API
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Parse the response and retrieve the comments
    data = response.json()
    comments = data["data"]["repository"]["issue"]["comments"]["edges"]

    # Process the comments
    for comment in comments:
        body = comment["node"]["bodyText"]
        author = comment["node"]["author"]["login"]
        print(f"Author: {author}")
        print(f"Comment: {body}\n")

    # Define the GraphQL query to retrieve the issue ID
    query_issue_id = """
    query GetIssueID {
    repository(owner: "%s", name: "%s") {
        issue(number: %s) {
        id
        }
    }
    }
    """ % (
        owner,
        name,
        issue_number,
    )

    # Send the GraphQL request to get the issue ID
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query_issue_id},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Parse the response and retrieve the issue ID
    data = response.json()
    issue_id = data["data"]["repository"]["issue"]["id"]

    # # Retrieve the issue ID for the update
    # issue_id = data["data"]["repository"]["issue"]["id"]

    # Define the updated issue title and body
    updated_title = "New Issue Title"
    updated_body = "New issue body content"

    # Define the GraphQL mutation to update the issue
    mutation = """
    mutation UpdateIssue {
    updateIssue(input: {id: "%s", title: "%s", body: "%s"}) {
        issue {
        title
        body
        }
    }
    }
    """ % (
        issue_id,
        updated_title,
        updated_body,
    )

    # Send the GraphQL mutation to the GitHub API
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": mutation},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Parse the response and retrieve the updated issue data
    data = response.json()
    updated_issue = data["data"]["updateIssue"]["issue"]

    # Print the updated issue details
    print("Updated Issue Details:")
    print(f'Title: {updated_issue["title"]}')
    print(f'Body: {updated_issue["body"]}')

    # Define the updated issue title and body
    updated_title = "updated title from code"
    updated_body = "updated body from code"

    # Define the GraphQL mutation to update the issue
    mutation_update_issue = """
    mutation UpdateIssue {
    updateIssue(input: {id: "%s", title: "%s", body: "%s"}) {
        issue {
        id
        title
        body
        }
    }
    }
    """ % (
        issue_id,
        updated_title,
        updated_body,
    )

    # Send the GraphQL mutation to update the issue
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": mutation_update_issue},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Parse the response and retrieve the updated issue data
    data = response.json()
    updated_issue = data["data"]["updateIssue"]["issue"]

    # Print the updated issue details
    print("Updated Issue Details:")
    print(f'Title: {updated_issue["title"]}')
    print(f'Body: {updated_issue["body"]}')

    # Define the new comment content
    new_comment_body = "This is a new comment."

    # Define the GraphQL mutation to add a new comment
    mutation_add_comment = """
    mutation AddComment {
    addComment(input: {subjectId: "%s", body: "%s"}) {
        commentEdge {
        node {
            body
            author {
            login
            }
        }
        }
    }
    }
    """ % (
        updated_issue["id"],
        new_comment_body,
    )

    # Send the GraphQL mutation to add a new comment
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": mutation_add_comment},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Parse the response and retrieve the new comment data
    data = response.json()
    new_comment = data["data"]["addComment"]["commentEdge"]["node"]

    # Print the new comment details
    print("New Comment Details:")
    print(f'Author: {new_comment["author"]["login"]}')
    print(f'Comment: {new_comment["body"]}')

    # test


def retrieve_issue_id(owner, name, issue_number, token):
    query = """
    query GetIssueID {
        repository(owner: "%s", name: "%s") {
        issue(number: %s) {
            id
        }
        }
    }
    """ % (
        owner,
        name,
        issue_number,
    )

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    issue_id = data["data"]["repository"]["issue"]["id"]
    return issue_id


def update_issue(issue_id, updated_title, updated_body, token):
    mutation = """
    mutation UpdateIssue {
      updateIssue(input: {id: "%s", title: "%s", body: "%s"}) {
        issue {
          title
          body
        }
      }
    }
    """ % (
        issue_id,
        updated_title,
        updated_body,
    )

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": mutation},
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    updated_issue = data["data"]["updateIssue"]["issue"]
    return updated_issue


def add_comment(issue_id, new_comment_body, token):
    mutation = """
    mutation AddComment {
      addComment(input: {subjectId: "%s", body: "%s"}) {
        commentEdge {
          node {
            body
            author {
              login
            }
          }
        }
      }
    }
    """ % (
        issue_id,
        new_comment_body,
    )

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": mutation},
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    new_comment = data["data"]["addComment"]["commentEdge"]["node"]
    return new_comment


# Load environment variables from .env file
load_dotenv()

# Define the test data
owner = os.getenv("OWNER")
name = os.getenv("REPO_NAME")
issue_number = os.getenv("ISSUE_NUMBER")
token = os.getenv("GITHUB_TOKEN")


def test_retrieve_issue_id():
    # Call the function to retrieve the issue ID
    issue_id = retrieve_issue_id(owner, name, issue_number, token)

    # Assert that the issue ID is not empty
    assert issue_id is not None


def test_update_issue():
    # Define the test data
    issue_id = retrieve_issue_id(owner, name, issue_number, token)
    updated_title = "New Issue Title"
    updated_body = "New issue body content"

    # Call the function to update the issue
    updated_issue = update_issue(issue_id, updated_title, updated_body, token)

    # Assert that the updated issue has the expected title and body
    assert updated_issue["title"] == updated_title
    assert updated_issue["body"] == updated_body


def test_add_comment():
    # Define the test data
    issue_id = retrieve_issue_id(owner, name, issue_number, token)
    new_comment_body = "This is a new comment."

    # Call the function to add a new comment
    new_comment = add_comment(issue_id, new_comment_body, token)

    # Assert that the new comment has the expected body
    assert new_comment["body"] == new_comment_body
    assert new_comment["author"]["login"] == owner


# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])
