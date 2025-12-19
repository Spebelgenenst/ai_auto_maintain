from github import Github
from github import Auth
import json

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

github_token = Auth.Token(credentials["githubToken"])
g = Github(auth=github_token)

repo = g.get_repo("spebelgenenst/ai_auto_maintain_test_repo")
file_path = "test.txt"

try:
    data = repo.get_contents(path=file_path, ref="h)
except:
    data = repo.get_contents(path=file_path)

print(data.decoded_content.decode())



#print(repo.get_branch(branch="ai_bugfixes"))

#contents = repo.get_contents("test.txt", ref="ai_bugfixes")

#repo.update_file(contents.path, "1", "2", contents.sha, branch="ai_bugfixes")
#repo.update_file(contents.path, "commit message", "content", contents.sha, branch="branch")

#open_issues = repo.get_issues(state='open')

#print(open_issues.totalCount)
#data = repo.get_contents(path="")
#print(data)
#for file in repo.get_contents(path=""):
#    print(file.decoded_content.decode())
#for issue in open_issues:
#    print(issue.title+issue.body)

g.close