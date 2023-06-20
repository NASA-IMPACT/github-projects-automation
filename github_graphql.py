import requests


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
