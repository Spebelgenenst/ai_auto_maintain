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

    with open("credentials.json", "r") as file:
        credentials = json.load(file)

except FileNotFoundError:
    print("Some File not found! Please follow the docs :3")
    quit()

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-2.5-flash" #"gemini-2.5-flash-lite"

github_token = Auth.Token(credentials["githubToken"])

class Ai():
    def get_declarations(self, local_file):
        update_github_file_declaration = {
            "name": "update_file",
            "description": "Updates a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "enum": local_file,
                        "description": "the name/path of the file that you want to change",
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "a short info of what you have changed",
                    },
                    "file_content": {
                        "type": "string",
                        "description": "the content you want to replace the old content with"
                    },
                },
                "required": ["file_path", "commit_message", "file_content"],
            },
        }

        get_file_declaration = {
            "name": "get_file",
            "description": "Gives you the file you need",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "enum": local_file,
                        "description": "the name/path of the file that you want",
                    }
                },
                "required": ["file_path"],
            },
        }

        end_cycle_declaration = {
            "name": "end_cycle",
            "description": "call this function if you are done",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_comment": {
                        "type": "string",
                        "description": "comment under the issue",
                    }
                },
                "required": ["issue_comment"],
            },
            
        }

        return self.tools_declaration([update_github_file_declaration, get_file_declaration, end_cycle_declaration])

    def tools_declaration(self, declaration):
        tools = types.Tool(function_declarations=declaration)
        return types.GenerateContentConfig(tools=[tools])

    def ai(self, ai_model, content, config):
        response = client.models.generate_content(
            model=ai_model,
            contents=content,
            config=config
        )
        return response
    
    def upload_file(self, local_file, repo):
        print("uploading file")

        uploaded_file = client.files.upload(file=f"{repo.name}/{local_file}")
        content = [uploaded_file]
        return content


class github_action():

    def update_file(self, file_path, commit_message, file_content, repo, ai_branch):
        print(f"updating file {file_path}")
        self.manage_branch(repo, ai_branch)
        content = repo.get_contents(file_path, ref=ai_branch)
        print(file_content)
        repo.update_file(content.path, commit_message, file_content, content.sha, branch=ai_branch)

    def manage_branch(self, repo, ai_branch):
        for branch in repo.get_branches():
            if branch.name == ai_branch:
                return
        main_branch = repo.get_branch("main")

        repo.create_git_ref(
            ref="refs/heads/" + ai_branch,
            sha=main_branch.commit.sha
        )

    def get_file(self, repo, file_path, ai_branch):
        print(f"downloading file {file_path}")
        try:
            data = repo.get_contents(path=file_path, ai_branch=ai_branch)
        except:
            data = repo.get_contents(path=file_path)
    
        local_file = file_path
        os.makedirs(repo.name, exist_ok=True)
        with open(f"{repo.name}/{file_path}", "w") as f:
            f.write(data.decoded_content.decode())
        return local_file


class Main():

    def ai_cycle(self, file_paths, issue, file, config, repo, ai_branch):
        content = prompt+"\n"+issue.title+"\n"+issue.body
        if file:
            content = [content, file]
        issue_done = False
        file = None

        print("waiting for ai response")
        response = Ai().ai(ai_model=ai_model, content=content, config=config)

        print("executing function calls")
        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            if function_call.name == "update_file":
                github_action().update_file(**function_call.args, repo=repo, ai_branch=ai_branch)

            if function_call.name == "get_file":
                local_file = github_action().get_file(**function_call.args, repo=repo, ai_branch=ai_branch)
                file = Ai().upload_file(local_file, repo=repo)

            if function_call.name == "end_cycle":
                print("end_cycle")
                issue.create_comment(function_call.args)
                issue.add_to_labels("ai bugfix done")
                issue_done = True

        
        return file, issue_done

    def __init__(self):
        with Github(auth=github_token) as g:
            repo = g.get_repo(credentials["repoName"])
            ai_branch = credentials["aiBugfixBranch"]

            while True:
                open_issues = repo.get_issues(state="open")

                for issue in open_issues:

                    if "ai bugfix done :3" in issue.get_labels():
                        continue
                    print("New issue")

                    file_paths = [file.path for file in repo.get_contents("")]
                    file = None
                    config = Ai().get_declarations(file_paths)
                    while True:
                        file, issue_done = self.ai_cycle(file_paths, issue, file, config, repo, ai_branch)
                        
                        if issue_done:
                            print("ai bugfix done :3")
                            break

                sleep(300)

if __name__ ==  "__main__":
    Main()
