from github import Github
from github import Auth
import json

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

github_token = Auth.Token(credentials["GithubToken"])
g = Github(auth=github_token)

repo = g.get_repo("kaibuzz0/Termux-Mobile-BAREIRON-server")

open_issues = repo.get_issues(state='open')

for issue in open_issues:
    print(issue)

g.close