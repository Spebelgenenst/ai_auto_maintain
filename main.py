import json
from google import genai
from google.genai import types
from github import Github
from github import Auth
from io import StringIO
from time import sleep
import os

try:
    with open("prompt.md", "r") as file:
        prompt = file.read()

    with open("prompt_get_files.md", "r") as file:
        prompt_get_files = file.read()

    with open("credentials.json", "r") as file:
        credentials = json.load(file)

except FileNotFoundError:
    print("Some File not found! Please follow the docs :33")
    quit()

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-2.5-flash" #"gemini-2.5-flash-lite" #

github_token = Auth.Token(credentials["githubToken"])

def get_get_files_declarations(local_files):
    get_file_declaration = {
        "name": "get_file",
        "description": "Gives you the file you need",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "enum": local_files,
                    "description": "the name/path of the file that you want",
                }
            },
            "required": ["file_path"],
        },
    }

    return update_github_file_declaration

def get_update_files_declarations(local_files):
    update_github_file_declaration = {
        "name": "update_file",
        "description": "Updates a file",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "enum": local_files,
                    "description": "the name/path of the file that you want to change",
                },
                "commit_message": {
                    "type": "string",
                    "description": "a short info of what you have changed",
                },
                "file_content": {
                    "type": "string",
                    "description": "The content you want to replace the old content with"
                },
            },
            "required": ["file_path", "commit_message", "file_content"],
        },
    }

    return update_github_file_declaration

def tools_declaration(declaration):
    tools = types.Tool(function_declarations=[declaration])
    return types.GenerateContentConfig(tools=[tools])


def update_github_file(file_path, commit_message, file_content):
    manage_branch()
    content = repo.get_contents(file_path)
    repo.update_file(contents.path, commit_message, file_content, contents.sha, branch="ai_bugfixes")

def ai(ai_model, content, config):
    response = client.models.generate_content(
        model=ai_model,
        contents=content,
        config=config
    )
    return response

def manage_branch():
    for branch in repo.get_branches():
        if branch.name == "ai_bugfixes":
            return
    main_branch = repo.get_branch("main")

    repo.create_git_ref(
        ref=f"refs/heads/ai_bugfixes",
        sha=main_branch.commit.sha
    )

def get_files():
    data = repo.get_contents(path="")
    local_files = []
    os.makedirs(repo.name, exist_ok=True)
    for file in data:
        local_files.append(file.path)
        with open(f"{repo.name}/{file.path}", "w") as f:
            f.write(file.decoded_content.decode())
    return local_files


def upload_files(local_files, content):
    try:
        for file in content:
            client.files.delete(file=f"{repo.name}/{file}")
    except:
        pass

    content = []
    for local_file in local_files:
        uploaded_file = client.files.upload(file=f"{repo.name}/{local_file}")
        content.append(uploaded_file)
    return content

    
def fix_issue(issue, content):
    content.append(prompt+"\n"+issue.title+"\n"+issue.body)
    print("waiting for ai to respond...")
    response = ai(ai_model, content, config=update_declarations(local_files)).text
    print(response)
    print("executing function calls")
    tool_call = response.candidates[0].content.parts[0].function_call

    if tool_call.name == "update_file":
        update_github_file(**tool_call.args)
        print("file updated")

    issue.create_comment("ai bugfix done")

def ask_for_files(issue, local_files):
    content = prompt+str(local_files)+"\n"+issue.title+"\n"+issue.body
    response = ai(ai_model=ai_model, content=content, config=None)
    local_files = get_files()
    content = upload_files(local_files, content)
    return content

if __name__ ==  "__main__":
    with Github(auth=github_token) as g:
        repo = g.get_repo(credentials["repoName"])

        while True:
            open_issues = repo.get_issues(state="open")

            for issue in open_issues:
                content = ask_for_files()
                fix_issue(issue, content)
                quit()

            sleep(300)
