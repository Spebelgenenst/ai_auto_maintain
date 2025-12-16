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

    with open("prompt_get_file.md", "r") as file:
        prompt_get_files = file.read()

    with open("credentials.json", "r") as file:
        credentials = json.load(file)

except FileNotFoundError:
    print("Some File not found! Please follow the docs :33")
    quit()

client = genai.Client(api_key=credentials["geminiApiKey"])

ai_model = "gemini-2.5-flash" #"gemini-2.5-flash-lite" #

github_token = Auth.Token(credentials["githubToken"])

class Ai():
    def get_get_files_declarations(self, files):
        get_file_declaration = {
            "name": "get_file",
            "description": "Gives you the file you need",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "enum": files,
                        "description": "the name/path of the file that you want",
                    }
                },
                "required": ["file_path"],
            },
        }

        return self.tools_declaration(get_file_declaration)

    def get_update_files_declarations(self, local_file):
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
                        "description": "The content you want to replace the old content with"
                    },
                },
                "required": ["file_path", "commit_message", "file_content"],
            },
        }

        return self.update_github_file_declaration(update_github_file_declaration)

    def tools_declaration(self, declaration):
        tools = types.Tool(function_declarations=[declaration])
        return types.GenerateContentConfig(tools=[tools])

    def ai(self, ai_model, content, config):
        response = client.models.generate_content(
            model=ai_model,
            contents=content,
            config=config
        )
        return response
    
    def upload_file(self, local_file):
        #try:
        #    for file in content:
        #        client.files.delete(file=f"{repo.name}/{file}")
        #except:
        #    pass

        uploaded_file = client.files.upload(file=f"{repo.name}/{local_file}")
        content = [uploaded_file]
        return content


class github_action():

    def update_file(self, file_path, commit_message, file_content):
        self.manage_branch()
        content = repo.get_contents(file_path)
        repo.update_file(contents.path, commit_message, file_content, contents.sha, branch="ai_bugfixes")

    def manage_branch(self):
        for branch in repo.get_branches():
            if branch.name == "ai_bugfixes":
                return
        main_branch = repo.get_branch("main")

        repo.create_git_ref(
            ref=f"refs/heads/ai_bugfixes",
            sha=main_branch.commit.sha
        )

    def get_files(self, file_path):
        data = repo.get_contents(path=file_path)
        local_file = [file_path]
        os.makedirs(repo.name, exist_ok=True)
        with open(f"{repo.name}/{file_path}", "w") as f:
            f.write(file.decoded_content.decode())
        return local_file


class Main():

    def fix_issue(self, issue, file):
        content = file
        content.append(prompt+"\n"+issue.title+"\n"+issue.body)
        print("waiting for ai to respond...")
        response = Ai.ai(ai_model, content, config=ai.get_update_files_declarations(file)).text
        print(response)
        print("executing function calls")

        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:
            if function_call.name == "update_file":
                github_action.update_file(**function_call.args)
                print("file updated")
        else:
            print("no function called")
            quit()
            

        issue.create_comment("ai bugfix done")

    def ask_for_files(self, issue, files):
        content = prompt+str(files)+"\n"+issue.title+"\n"+issue.body
        config = Ai().get_get_files_declarations(files=files)
        print(config)
        response = Ai().ai(ai_model=ai_model, content=content, config=config)

        function_call = response.candidates[0].content.parts[0].function_call
        if function_call:

            if function_call.name == "get_file":
                local_file = github_action.get_file(**function_call.args)
                print("file downloaded")
                file = Ai.upload_file(local_file)
                print("file uploaded")
        else:
            print("no function called")
            quit()

        return file

    def __init__(self):
        with Github(auth=github_token) as g:
            repo = g.get_repo(credentials["repoName"])

            while True:
                open_issues = repo.get_issues(state="open")

                for issue in open_issues:
                    file_paths = [file.path for file in repo.get_contents("")]
                    content = self.ask_for_files(issue=issue, files=file_paths)
                    self.fix_issue(issue, content)
                    quit()

                sleep(300)

if __name__ ==  "__main__":
    Main()