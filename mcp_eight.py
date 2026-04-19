from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()
# 🔐 Put your GitHub personal access token here
GITHUB_PAT = os.getenv("GITHUB_PAT")  # Set this in your .env file  



# 🔐 Create a GitHub Personal Access Token (Classic) here:
# 👉 https://github.com/settings/tokens/new
# Recommended minimal scopes for read-only MCP testing:
#   ✅ read:user   → allows retrieving your username & profile
#   ✅ public_repo → allows reading your public repositories
# (If you want to manage private repos later, also add: repo)

client = OpenAI()

resp = client.responses.create(
    model="gpt-5-mini",   # small model = cheaper + faster
    tools=[{
        "type": "mcp",
        "server_label": "github",
        "server_description": "GitHub MCP server test",
        "server_url": "https://api.githubcopilot.com/mcp/",
        "headers": {
            "Authorization": f"Bearer {GITHUB_PAT}"
        },
        "require_approval": "never",
    }],
    input="Show my GitHub username using the GitHub MCP server.",
)

# print(resp.output_text)


resp = client.responses.create(
    model="gpt-5-nano",
    tools=[{
        "type": "mcp",
        "server_label": "github",
        "server_url": "https://api.githubcopilot.com/mcp",
        "headers": {"Authorization": f"Bearer {GITHUB_PAT}"},
        "require_approval": "never",
    }],
    input="List public repositories for the user 'farhan-fk' with their descriptions. Output as a short plain-text list.",
)
print(resp.output_text)
