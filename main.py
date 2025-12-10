import json
from google import genai
from github import Github
from github import Auth
import StringIO
from time import sleep

#with open('prompt.md', 'r') as file:
#    prompt = file.read()

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-3-pro-preview"

github_token = Auth.Token(credentials["GithubToken"])
g = Github(auth=github_token)

repo = g.get_repo("spebelgenenst/ai_auto_maintain_test_repo")

def ai(ai_model, prompt):
    response = client.models.generate_content(
        model=ai_model,
        contents=prompt
    )

    return response

def get_files():
    file_list = json.load(repo.get_contents(path=".auto_maintain.json"))

def fix_issue(issue):

    print("waiting for ai to respond...")
    response = ai(ai_model, prompt).text
    if not response:
        return


if __name__ ==  "__main__":
    while True:
        open_issues = repo.get_issues(state='open')
        for issue in open_issues:
            fix_issue()
        sleep(30)
