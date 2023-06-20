from github_graphql import get_viewer_login

personal_access_token = "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"

viewer_login = get_viewer_login(personal_access_token)
print(f"Authenticated as: {viewer_login}")
