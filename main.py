import json
from google import genai
from github import Github
from github import Auth
from io import StringIO
from time import sleep

#with open('prompt.md', 'r') as file:
#    prompt = file.read()

with open('credentials.json', 'r') as file:
    credentials = json.load(file)

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-3-pro-preview"

github_token = Auth.Token(credentials["githubToken"])
g = Github(auth=github_token)

repo = g.get_repo("spebelgenenst/ai_auto_maintain_test_repo")

def ai(ai_model, prompt, files):
    response = client.models.generate_content(
        model=ai_model,
        contents=[prompt,str(files)]
    )

    return response

def get_files():
    data = repo.get_contents(path="")
    files = []
    for file in data:
        files.append([file.path,file.content])
    return files

def fix_issue(issue):
    print("getting files from github...")
    files = get_files()
    print("waiting for ai to respond...")
    response = ai(ai_model, prompt, files).text
    print(response)


if __name__ ==  "__main__":
    fix_issue("test")
    while True:
        open_issues = repo.get_issues(state='open')
        for issue in open_issues:
            fix_issue(issue)
        sleep(300)
