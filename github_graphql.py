import json
import requests
from enum import Enum
from dotenv import dotenv_values
import os
import pytest
from dotenv import load_dotenv
from datetime import datetime


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


def get_all_issues(owner, name, token):
    query = """
    query GetAllIssues {
      repository(owner: "%s", name: "%s") {
        issues(first: 100) {
          edges {
            node {
              title
              bodyText
              author {
                login
              }
            }
          }
        }
      }
    }
    """ % (
        owner,
        name,
    )

    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"},
    )

    data = response.json()
    issues = data["data"]["repository"]["issues"]["edges"]

    # Extract relevant data for each issue
    result = []
    for issue in issues:
        title = issue["node"]["title"]
        body = issue["node"]["bodyText"]
        author = issue["node"]["author"]["login"]
        result.append({"title": title, "body": body, "author": author})

    return result


def fetch_comments_of_issue_and_update(token, issue_number, owner, name):
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


# logic to retrieve open and closed issues, assignees, and completion time
def get_all_issues_details(owner, name, token):
    query = """
    query GetAllIssues {
      repository(owner: "%s", name: "%s") {
          issues(first: 100) {
      nodes {
        createdAt
        closedAt
        title
        assignees(first: 1) {
          nodes {
            login
          }
        }
      }
    }
        
      }
    }
    """ % (
        owner,
        name,
    )
    # Define headers with authorization
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    url = "https://api.github.com/graphql"
    # Make the API request
    response = requests.post(url, json={"query": query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        issues = data["data"]["repository"]["issues"]["nodes"]
        total_issues_count = len(issues)

        print(f"Number of issues: {total_issues_count}")

        for issue in issues:
            created_at = datetime.strptime(issue["createdAt"], "%Y-%m-%dT%H:%M:%SZ")

            if issue["closedAt"]:
                closed_at = datetime.strptime(issue["closedAt"], "%Y-%m-%dT%H:%M:%SZ")
                completion_time = closed_at - created_at
                completion_hours = completion_time.total_seconds() / 3600

                assignees = issue["assignees"]["nodes"]
                if assignees:
                    assignee = assignees[0]["login"]
                else:
                    assignee = "Unassigned"

                print(
                    f"Issue '{issue['title']}' assigned to {assignee} took {completion_hours:.2f} hours to complete"
                )
            else:
                current_time = datetime.utcnow()
                time_taken = current_time - created_at
                time_taken_hours = time_taken.total_seconds() / 3600

                assignees = issue["assignees"]["nodes"]
                if assignees:
                    assignee = assignees[0]["login"]
                else:
                    assignee = "Unassigned"

                print(
                    f"Issue '{issue['title']}' assigned to {assignee} is open for {time_taken_hours:.2f} hours"
                )
    else:
        print(f"Request failed with status code {response.status_code}")


# to fetch PR data with limited comments per PR
def get_PR_Metrics(owner, name, token):
    query = """
    query GetAllIssues {
      repository(owner: "%s", name: "%s") {
     pullRequests(first: 100) {
      nodes {
        createdAt
        mergedAt
        reviews(first: 100) {
          nodes {
            createdAt
            state
            comments(first: 10) {
              totalCount
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
    )

    # Define headers with authorization
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    url = "https://api.github.com/graphql"

    # Make the API request
    response = requests.post(url, json={"query": query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Check if 'data' key is present in the response
        if "data" in data:
            pull_requests = data["data"]["repository"]["pullRequests"]["nodes"]
            total_prs = len(pull_requests)
            total_review_time = 0
            total_merge_time = 0
            total_iterations = 0
            total_comments = 0

            for pr in pull_requests:
                created_at = datetime.strptime(pr["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
                merged_at = (
                    datetime.strptime(pr["mergedAt"], "%Y-%m-%dT%H:%M:%SZ")
                    if pr["mergedAt"]
                    else None
                )

                if merged_at:
                    pr_iterations = len(pr["reviews"]["nodes"])
                    total_iterations += pr_iterations

                    comments_count = sum(
                        review["comments"]["totalCount"]
                        for review in pr["reviews"]["nodes"]
                        if review["state"] == "COMMENTED"
                    )
                    total_comments += comments_count

                    review_time = (
                        merged_at - created_at
                    ).total_seconds() / 3600  # in hours
                    merge_time = (
                        merged_at - created_at
                    ).total_seconds() / 3600  # in hours

                    total_review_time += review_time
                    total_merge_time += merge_time

            # Calculate the average metrics
            avg_comments_per_pr = total_comments / total_prs if total_prs > 0 else 0
            avg_review_time = total_review_time / total_prs if total_prs > 0 else 0
            avg_merge_time = total_merge_time / total_prs if total_prs > 0 else 0
            avg_iterations = total_iterations / total_prs if total_prs > 0 else 0

            # Print the metrics
            print(f"Average number of comments per PR: {avg_comments_per_pr:.2f}")
            print(f"Average review time: {avg_review_time:.2f} hours")
            print(f"Average merge time: {avg_merge_time:.2f} hours")
            print(f"Average iterations per PR: {avg_iterations:.2f}")
        else:
            print("Data not found in the response.")
            print(f"Response content: {response.content.decode('utf-8')}")
    else:
        print(f"Request failed with status code {response.status_code}")


#
def issue_management_metrics_calculation(owner, name, token):
    query = """
    query {
      repository(owner: "%s", name: "%s") {
     issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes {
        createdAt
        closedAt
        title
        priority: labels(first: 1) {
          nodes {
            name
          }
        }
        assignees(first: 1) {
          nodes {
            login
          }
        }
      }
    }
      }
    }
    """ % (
        owner,
        name,
    )
    url = "https://api.github.com/graphql"
    # Define headers with authorization
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # Make the API request
    response = requests.post(url, json={"query": query}, headers=headers)
    print(response.json())
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the necessary data from the response
        issues = data["data"]["repository"]["issues"]["nodes"]
        total_issues = len(issues)
        total_resolution_time = 0
        total_time_to_assign = 0
        priority_counts = {}
        assignee_counts = {}

        for issue in issues:
            created_at = datetime.strptime(issue["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
            closed_at = (
                datetime.strptime(issue["closedAt"], "%Y-%m-%dT%H:%M:%SZ")
                if issue["closedAt"]
                else None
            )

            if closed_at:
                resolution_time = closed_at - created_at
                total_resolution_time += resolution_time.total_seconds() / 3600

            assignees = issue["assignees"]["nodes"]
            if assignees:
                assignee = assignees[0]["login"]
                time_to_assign = (
                    created_at
                    - datetime.strptime(issue["createdAt"], "%Y-%m-%dT%H:%M:%SZ")
                ).total_seconds() / 3600
                total_time_to_assign += time_to_assign
                assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1

            priority = (
                issue["priority"]["nodes"][0]["name"]
                if issue["priority"]["nodes"]
                else "Uncategorized"
            )
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Calculate the metrics
        avg_resolution_time = (
            total_resolution_time / total_issues if total_issues > 0 else 0
        )
        avg_time_to_assign = (
            total_time_to_assign / total_issues if total_issues > 0 else 0
        )

        # Print the metrics
        print(f"Average resolution time: {avg_resolution_time:.2f} hours")
        print(f"Average time to assign: {avg_time_to_assign:.2f} hours")
        print("Priority distribution:")
        for priority, count in priority_counts.items():
            print(f"{priority}: {count}")
        print("Assignee distribution:")
        for assignee, count in assignee_counts.items():
            print(f"{assignee}: {count}")
    else:
        print(f"Request failed with status code {response.status_code}")


def project_activity_metrics_calculation(owner, name, token):
    query = """
    query {
      repository(owner: "%s", name: "%s") {
  refs(refPrefix: "refs/heads/", first: 1) {
      nodes {
        target {
          ... on Commit {
            history(first: 100) {
              totalCount
              nodes {
                committedDate
                author {
                  user {
                    login
                  }
                }
              }
            }
          }
        }
      }
    }
    pullRequests {
      totalCount
    }
    issues {
      totalCount
    }
      }
    }
    """ % (
        owner,
        name,
    )
    url = "https://api.github.com/graphql"
    # Define headers with authorization
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # Make the API request
    response = requests.post(url, json={"query": query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the necessary data from the response
        refs = data["data"]["repository"]["refs"]["nodes"]
        pull_requests_count = data["data"]["repository"]["pullRequests"]["totalCount"]
        issues_count = data["data"]["repository"]["issues"]["totalCount"]

        if not refs:
            print("No default branch found in the repository.")
        else:
            commit_history = refs[0]["target"]["history"]["nodes"]

            contributor_commits = {}

            for commit in commit_history:
                login = owner
                #             author =
                if login == owner:
                    if login in contributor_commits:
                        contributor_commits[login] += 1
                    else:
                        contributor_commits[login] = 1

            # Sort the contributors based on commit count
            sorted_contributors = sorted(
                contributor_commits.items(), key=lambda x: x[1], reverse=True
            )
            #         print("sorted_contributors", sorted_contributors)
            # Extract the top 5 active contributors
            top_active_contributors = sorted_contributors[:1]

            # Extract the top 5 passive contributors (remaining contributors)
            top_passive_contributors = sorted_contributors[1:]

            # Print the project activity metrics
            print("Project Activity Metrics:")
            print(f"Total Commits: {len(commit_history)}")
            print(f"Total Pull Requests: {pull_requests_count}")
            print(f"Total Issues: {issues_count}")
            print(f"Top 5 Active Contributors:")
            for contributor, commit_count in top_active_contributors:
                print(f"{contributor}: {commit_count} commits")
            print(f"Top 5 Passive Contributors:")
            for contributor, commit_count in top_passive_contributors:
                print(f"{contributor}: {commit_count} commits")
    else:
        print(f"Request failed with status code {response.status_code}")


def contributor_activity_metrics_calculation(owner, name, token):
    query = """
    query {
      repository(owner: "%s", name: "%s") {
   pullRequests(states: [OPEN, CLOSED], first: 100) {
      totalCount
      nodes {
        author {
          login
        }
        comments {
          totalCount
        }
      }
    }
    issues(states: [OPEN, CLOSED], first: 100) {
      totalCount
      nodes {
        author {
          login
        }
        comments {
          totalCount
        }
      }
    }
      }
    }
    """ % (
        owner,
        name,
    )
    url = "https://api.github.com/graphql"
    # Define headers with authorization
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    # Make the API request
    response = requests.post(url, json={"query": query}, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()

        # Extract the necessary data from the response
        pull_requests = data["data"]["repository"]["pullRequests"]["nodes"]
        issues = data["data"]["repository"]["issues"]["nodes"]

        # Track contribution metrics
        contributor_activity = {}

        for pr in pull_requests:
            author = pr["author"]["login"]
            comments = pr["comments"]["totalCount"]

            if author not in contributor_activity:
                contributor_activity[author] = {
                    "pull_requests": 0,
                    "comments": 0,
                    "issues": 0,
                }

            contributor_activity[author]["pull_requests"] += 1
            contributor_activity[author]["comments"] += comments

        for issue in issues:
            author = issue["author"]["login"]
            comments = issue["comments"]["totalCount"]

            if author not in contributor_activity:
                contributor_activity[author] = {
                    "pull_requests": 0,
                    "comments": 0,
                    "issues": 0,
                }

            contributor_activity[author]["issues"] += 1
            contributor_activity[author]["comments"] += comments

        # Print the contribution activity metrics
        print("Contribution Activity Metrics:")
        for contributor, activity in contributor_activity.items():
            print(f"Contributor: {contributor}")
            print(f"Pull Requests: {activity['pull_requests']}")
            print(f"Issues: {activity['issues']}")
            print(f"Comments: {activity['comments']}")
            print("-" * 30)
    else:
        print(f"Request failed with status code {response.status_code}")


# Helper function to format metadata fields as a Markdown list
def format_metadata_fields(fields):
    markdown_list = "\n"
    for key, value in fields.items():
        markdown_list += f"- **{key}:** {value}\n"
    return markdown_list


def add_metadata_to_project_board(owner, name, token, project_id):
    query = """
    query {
      repository(owner: "%s", name: "%s") {
   mutation ($input: UpdateProjectInput!) {
  updateProject(input: $input) {
    project {
      id
      body
    }
  }
}
      }
    }
    """ % (
        owner,
        name,
    )
    url = "https://api.github.com/graphql"
    # Define the metadata fields you want to add
    metadata_fields = {"Field 1": "Value 1", "Field 2": "Value 2", "Field 3": "Value 3"}

    # Prepare the GraphQL variables
    variables = {
        "input": {
            "projectId": project_id,
            "body": format_metadata_fields(metadata_fields),
        }
    }
    # Prepare the request headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.starfire-preview+json",
    }

    # Send the GraphQL mutation request
    response = requests.post(
        f"https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers,
    )

    # Check if the request was successful
    if response.status_code == 200:
        print("Metadata fields added successfully.")
    else:
        print("Failed to add metadata fields.")


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
