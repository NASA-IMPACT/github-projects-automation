from github_graphql import get_viewer_login
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

import os

# Access the token value
personal_access_token = os.getenv("TOKEN_SECRET")

viewer_login = get_viewer_login(personal_access_token)
print(f"Authenticated as: {viewer_login}")
