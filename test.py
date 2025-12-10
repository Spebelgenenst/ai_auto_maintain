from github import Github
from github import Auth
import json

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

github_token = Auth.Token(credentials["GithubToken"])
g = Github(auth=github_token)

repo = g.get_repo("Spebelgenenst/ai-experiment")

open_issues = repo.get_issues(state='open')

print(open_issues)

g.close