import json
from google import genai
from github import Github
from github import Auth
from io import StringIO
from time import sleep
import os

with open('prompt.md', 'r') as file:
    prompt = file.read()

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-3-pro-preview"

github_token = Auth.Token(credentials["githubToken"])

repo = g.get_repo("spebelgenenst/ai_auto_maintain_test_repo")

def ai(ai_model, content):
    response = client.models.generate_content(
        model=ai_model,
        contents=content
    )

    return response


def get_files():
    data = repo.get_contents(path="")
    local_files = []
    os.makedirs(repo.name, exist_ok=True)
    for file in data:
        local_files.append(f"{repo.name}/{file.path}")
        with open(f"{repo.name}/{file.path}", "w") as f:
            f.write(file.decoded_content.decode())
    return local_files


def upload_files(local_files):
    content = []
    for local_file in local_files:
        uploaded_file = client.files.upload(file=local_file)
        content.append(uploaded_file)
    return content

    
def fix_issue(issue):
    print("getting files from github...")
    local_files = get_files()
    content = upload_files(local_files)
    content.append(issue.title)
    content.append(issue.body)
    content.append(prompt)
    print("waiting for ai to respond...")
    response = ai(ai_model, content).text
    print(response)


if __name__ ==  "__main__":
    with Github(auth=github_token) as g:
        fix_issue("test")

        while True:
            open_issues = repo.get_issues(state='open')
            for issue in open_issues:
                fix_issue(issue)
            sleep(300)
