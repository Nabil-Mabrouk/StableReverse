import os
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline
import streamlit as st
from github import Github
import openai
from PIL import Image 
import git
from io import StringIO
from dotenv import load_dotenv
load_dotenv()

# Define your OpenAI GPT-3 API key
openai.api_key = os.getenv("OPENAI_KEY")
github_token=os.getenv("GITHUB_TOKEN")
ACCESS_KEY = os.getenv("ACCESS_KEY")

class Model():
    def __init__(self, model_name):
        self.model_name=model_name
        self.tokenizer=AutoTokenizer.from_pretrained(model_name, token=ACCESS_KEY)
        self.model = AutoModelForCausalLM.from_pretrained(model_name,  trust_remote_code=True,torch_dtype="auto",token= ACCESS_KEY)
        self.coder = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, max_new_tokens=4000)
    
    def generate(self,instructions):
        res = self.coder(instructions)
        return res[0]['generated_text']

def list_python_files(root_dir):
    python_files = []

    def traverse_directory(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir():
                    traverse_directory(entry.path)
                elif entry.is_file() and entry.name.endswith(".py"):
                    python_files.append(entry.path)

    traverse_directory(root_dir)
    return python_files

def python_files_to_string(file_list):
    return "\n".join(file_list)

def get_repo_description(repo_url, github_token):
    g = Github(github_token)
    repo = g.get_repo(repo_url.replace("https://github.com/", ""))
    return repo.description

def clone_github_repo(repo_url, root_dir):
    try:
        # Check if the root directory exists, create it if not
        if not os.path.exists(root_dir):
            os.makedirs(root_dir)

        # Clone the GitHub repository to the specified directory
        repo_path = os.path.join(root_dir, os.path.basename(repo_url))
        repo = git.Repo.clone_from(repo_url, repo_path)
        return root_dir
    except Exception as e:
        return str(e)

def classify_files_by_importance(repo_description, python_files, max_tokens=1000):
    prompt = f"Classify the importance of Python files in this repository based on the description:\n"
    prompt=prompt +f"{repo_description}\nPython files:\n{python_files}\n"
    prompt= prompt + f"You must answer by a bullet list of the files names starting from the most important." 
    prompt=prompt + "Do not add anythink else to your answer. Make sure to answer with the full name of the files"
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.7,
    )

    return response.choices[0].text

def display_file_content(selected_file):
    try:
        # To read file as string:
        stringio = StringIO(selected_file.getvalue().decode("utf-8"))
        string_data = stringio.read()

        st.subheader("Selected File Content:")
        st.code(string_data, language="python")
        return string_data
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

def main():
    st.title('⛵ StableReverse')
    image = Image.open('StableReverse.png')
    st.image(image)

    root_directory = st.text_input("Enter the root directory path:")
    github_repo_url = st.text_input("Enter the GitHub repo URL:","https://github.com/AntonOsika/gpt-engineer")

    if st.button("Clone GitHub Repo"):
        if not github_token:
            st.error("Please enter your GitHub token.")
        else:
            repo_path = clone_github_repo(github_repo_url, root_directory)
            if isinstance(repo_path, str):
                st.success(f"Repository cloned to {repo_path}")
                root_directory = repo_path
            else:
                st.error(f"Failed to clone repository: {repo_path}")


    if st.button("List Python Files"):
        if not os.path.isdir(root_directory):
            st.error("Invalid directory path.")
        else:
            python_files = list_python_files(root_directory)
            python_files_string = python_files_to_string(python_files)

            st.subheader("Python Files:")
            st.text_area(label="List of Python Files", value=python_files_string, height=400)

    if st.button("Get Repo Description"):
        if not github_token:
            st.error("Please enter your GitHub token.")
        else:
            repo_description = get_repo_description(github_repo_url, github_token)
            st.subheader("Repository Description:")
            st.text(repo_description)

    if st.button("Classify Files by Importance"):
        if not github_token:
            st.error("Please enter your GitHub token.")
        else:
            repo_description = get_repo_description(github_repo_url, github_token)
            python_files = list_python_files(root_directory)
            python_files_string = python_files_to_string(python_files)

            importance_classification = classify_files_by_importance(repo_description, python_files_string)
            st.subheader("File Importance Classification:")
            st.text(importance_classification)
    
    # Add a file uploader widget to select a file
    selected_file = st.file_uploader("Select a Python file from the root directory", type=["py"])

    if selected_file:
        data=display_file_content(selected_file)
        if st.button("Reverse Engineer"):
            # initialize model
                #model_name="stabilityai/stablecode-completion-alpha-3b" 
                model_name="stabilityai/stablecode-instruct-alpha-3b"
                st.header(f"Loading the model:")
                st.text(model_name)
                st.text("Loading model .. this may take few minutes")
                # Create the model
                model=Model(model_name)
                st.text("Model loaded successfuly!")
                prompt=f"### Instructions: \n Can you explain how this code works?\n Code: ### \n{data} \n ###\n End of the instructions"
                if(model):
                    try:
                        output=model.generate(prompt)
                        st.text("I got an answer to your request")
                    except Exception as e:
                        print("Error while running the model:", str(e))
                        st.text(str(e))


if __name__ == "__main__":
    main()
