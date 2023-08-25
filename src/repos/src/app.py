from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import pipeline
from dotenv import load_dotenv
import os, subprocess, shutil, json
import streamlit as st
from PIL import Image

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")

class Model():
    def __init__(self, model_name):
        self.model_name=model_name
        self.tokenizer=AutoTokenizer.from_pretrained(model_name, token=ACCESS_KEY)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, token= ACCESS_KEY)
        self.coder = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, max_new_tokens=100)
    
    def generate(self,instructions):
        res = self.coder(instructions)
        return res[0]['generated_text']

class Repo():
    def __init__(self, repo_url, local_folder):
        self.repo_url=repo_url
        self.local_folder=local_folder
    
    def clone(self):
        try:
            # Check if the local folder exists, if so, delete it
            if os.path.exists(local_folder):
                shutil.rmtree(local_folder)

            # Create the local folder
            os.makedirs(local_folder)
            # Clone the repository to the local folder
            subprocess.check_call(["git", "clone", self.repo_url, self.local_folder])
            print(f"Repository cloned to {self.local_folder}")
        except Exception as e:
            print(f"Error cloning repository: {e}")


    def get_file_system(self):
        file_system = {}

        for root, dirs, files in os.walk(self.local_folder):
            if root == self.local_folder:
                file_system[root] = dirs + files
            else:
                # Calculate the relative path from the local_folder
                relative_path = os.path.relpath(root, self.local_folder)
                relative_path_parts = relative_path.split(os.path.sep)

                # Initialize the current position in the file system dictionary
                current_position = file_system

                # Traverse the relative path and update the file system dictionary
                for part in relative_path_parts:
                    if part not in current_position:
                        current_position[part] = {}
                    current_position = current_position[part]

                # Add the files in the current directory to the dictionary
                current_position.update({os.path.basename(root): files})

        return file_system

if __name__ == "__main__":

    st.title('⛵ StableReverse')
    image = Image.open('StableReverse.png')
    st.image(image)
   
    model_name="stabilityai/stablecode-instruct-alpha-3b" 
    st.header(f"Model:")
    st.text(model_name)

    st.header(f"GitHub Repository:")
    repo_url = "https://github.com/AntonOsika/gpt-engineer"
    repo_url=st.text_input('Enter a valid GitHub reposotory url: ', 'https://github.com/Nabil-Mabrouk/StableReverse')
    local_folder="repos"

    if st.button("OK") and not st.button("stop"):
        # Create the model
        model=Model(model_name)
        repo=Repo(repo_url, local_folder)
        repo.clone()
        file_system=repo.get_file_system()
        st.header("FileSystem of the repo")
        st.text(json.dumps(file_system, indent=4))
        
        output="The code failed to generate an output"

        prompt=f"This is a filesystem for a github reposotory. Can you list the main python files? \n ### Filesystem: {file_system}\n #### You answer:"
        try:
            output=model.generate(prompt)
        except Exception as e:
            print("Error while querying the model", str(e))
            st.text(str(e))

        st.header("Model output:")
        st.text(output)

        print(output)





    