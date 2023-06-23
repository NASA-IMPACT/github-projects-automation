import requests
import json


def get_viewer_login(personal_access_token):
    # Define the GraphQL query or mutation you want to make
    graphql_query = """
        query {
            viewer {
                login
            }
        }
    """

    # Set the headers for the request
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }

    # Set the GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Send the GraphQL request
    response = requests.post(url, json={"query": graphql_query}, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            # Handle GraphQL errors
            for error in data["errors"]:
                print(f"GraphQL error: {error['message']}")
        else:
            # Extract the desired data from the response
            viewer_login = data["data"]["viewer"]["login"]
            return viewer_login
    else:
        # Handle request errors
        print(f"Request failed with status code: {response.status_code}")


def fetch_cards(personal_access_token, BOARD_URL, owner, repo_name):
    board_id = BOARD_URL.split("/")[-3]  # Provide the board_id
    owner = ""
    repo_name = ""
    # Define the GraphQL query or mutation you want to make
    graphql_query_fetch_cards = """
        query {
        repository(owner: <owner-name>, name:<repo-nanme>) {
            project(number: <board_id>) {
            columns(first: 2) {
                nodes {
                name
                cards(first: 2) {
                    nodes {
                    content {
                        ... on Issue {
                        title,
                        body,
                        closedAt
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

    # Set the GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Send the GraphQL request
    response = requests.post(
        url, json={"query": graphql_query_fetch_cards}, headers=headers
    )
    data = response.json()
    return data


def fetch_issues(
    personal_access_token, BOARD_URL, login, repo_name, desired_states, conditions_str
):
    board_id = BOARD_URL.split("/")[-3]  # Provide the board_id
    # Define the GraphQL query or mutation you want to make
    graphql_query_fetch_issues = """
        query {
       repository(owner: "{login}", name: "{repo_name}") {
            issues(first: 10, orderBy: { field: CREATED_AT, direction: DESC }, filterBy: { states ,conditions_str}) {
                nodes {
                    title,
                    body,
                    closedAt
                   
            }}
        }
    }
    """

    # Set the headers for the request
    headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }

    # Set the GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Send the GraphQL request
    response = requests.post(
        url, json={"query": graphql_query_fetch_issues}, headers=headers
    )
    data = response.json()
    return data


def update_metadata(
    personal_access_token,
    BOARD_URL,
    login,
    repo_name,
    issue_number,
    updated_assignee,
    updated_milestone,
    updated_labels,
    metadata_list,
):
    board_id = BOARD_URL.split("/")[-3]  # Provide the board_id
    # Define the GraphQL query or mutation you want to make
    query_issue = """
        query($issue_number: Int!) {
        repository(owner: "your_username", name: "your_repository(repo-name)") {
            issue(number: $issue_number) {
            id
            assignee {
                login
            }
            milestone {
                title
            }
            labels(first: 100) {
                nodes {
                name
                }
            }
            }
        }
        }
        """

    # GraphQL mutation to update the issue metadata
    mutation_update_metadata = """
    mutation($issue_id: ID!, $assignee: String, $milestone: String, $labels: [String], $metadata: [String]) {
    updateIssue(input: {id: $issue_id, assignee: $assignee, milestone: $milestone, labels: $labels}) {
        issue {
        id
        }
    }
    }
    """

    # Make the GraphQL query to fetch the issue
    variables = {"issue_number": issue_number}

    # Set the headers for the request
    # Create a session with the access token
    session = requests.Session()
    session.headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }

    # Set the GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Send the GraphQL request
    response = session.post(url, json={"query": query_issue, "variables": variables})
    data = json.loads(response.text)

    # Extract current metadata from the fetched issue
    issue_id = data["data"]["repository"]["issue"]["id"]
    current_assignee = data["data"]["repository"]["issue"]["assignee"]["login"]
    current_milestone = data["data"]["repository"]["issue"]["milestone"]["title"]
    current_labels = [
        label["name"]
        for label in data["data"]["repository"]["issue"]["labels"]["nodes"]
    ]

    # Update the metadata if they have changed
    if (
        current_assignee != updated_assignee
        or current_milestone != updated_milestone
        or current_labels != updated_labels
    ):
        # Prepare the variables for the update mutation
        variables = {
            "issue_id": issue_id,
            "assignee": updated_assignee,
            "milestone": updated_milestone,
            "labels": updated_labels,
            "metadata": metadata_list,
        }

        # Make the GraphQL mutation to update the issue metadata
        response = session.post(
            url, json={"query": mutation_update_metadata, "variables": variables}
        )

        if response.status_code == 200:
            print("Metadata updated successfully.")
        else:
            print("Failed to update metadata.")

    else:
        print("Metadata is already up to date.")


def fetch_issue_comments(
    personal_access_token, BOARD_URL, login, repo_name, issue_number
):
    board_id = BOARD_URL.split("/")[-3]  # Provide the board_id
    # Define the GraphQL query or mutation you want to make
    # GraphQL query to fetch issue comments
    query_comments = """
    query($issue_number: Int!) {
    repository(owner: "your_username", name: "your_repository") {
        issue(number: $issue_number) {
        id
        comments(first: 100) {
            nodes {
            id
            body
            }
        }
        }
    }
    }
    """
    url = "https://api.github.com/graphql"
    # Create a session with the access token
    session = requests.Session()
    session.headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }

    # Make the GraphQL query to fetch issue comments
    variables = {"issue_number": issue_number}
    response = session.post(url, json={"query": query_comments, "variables": variables})
    data = json.loads(response.text)

    comments = data["data"]["repository"]["issue"]["comments"]["nodes"]
    return json.dumps(comments)


# Function to add a new comment to an issue
def add_comment(personal_access_token, issue_number, comment_body):
    # Create a session with the access token
    session = requests.Session()
    session.headers = {
        "Authorization": f"Bearer {personal_access_token}",
        "Content-Type": "application/json",
    }

    # Make the GraphQL mutation to add a new comment
    query_issue = """
    query($issue_number: Int!) {
      repository(owner: "your_username", name: "your_repository") {
        issue(number: $issue_number) {
          id
        }
      }
    }
    """

    # GraphQL mutation to add a new comment to an issue
    mutation_add_comment = """
    mutation($issue_id: ID!, $body: String!) {
    addComment(input: {subjectId: $issue_id, body: $body}) {
        comment {
        id
        body
        }
    }
    }
    """
    url = "https://api.github.com/graphql"
    variables = {"issue_number": issue_number}
    response = session.post(url, json={"query": query_issue, "variables": variables})
    data = json.loads(response.text)
    issue_id = data["data"]["repository"]["issue"]["id"]

    variables = {"issue_id": issue_id, "body": comment_body}
    response = session.post(
        url, json={"query": mutation_add_comment, "variables": variables}
    )

    if response.status_code == 200:
        print("New comment added successfully.")
    else:
        print("Failed to add comment.")
