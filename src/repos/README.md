# StableReverse
## Reverse Engineering of gitHub project

![GitHub Logo](img/StableReverse.png)

## Overview

This project is designed to help you reverse engineer GitHub projects with ease. It leverages the power of StableCode-16K model to analyze project repositories, review and improve the code

## Steps

- **Repository Cloning:** Clone GitHub repositories to your local machine directly from the web interface.
```python
import os
import subprocess

# Function to clone a GitHub repository
def clone_github_repo(repo_url, local_folder):
    try:
        # Check if the local folder exists, if not, create it
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        # Clone the repository to the local folder
        subprocess.check_call(["git", "clone", repo_url, local_folder])
        print(f"Repository cloned to {local_folder}")
    except Exception as e:
        print(f"Error cloning repository: {e}")

# Ask the user for the GitHub repository URL
repo_url = input("Enter the GitHub repository URL: ")

# Specify the local folder where you want to clone the repository
local_folder = "local_repo"  # You can change this to your preferred folder name

# Clone the GitHub repository
clone_github_repo(repo_url, local_folder)
```
- **File System Analysis:** Automatically extract and analyze the file and folder structure of the cloned repository (Tree representation of the file system)

```python
import os
import json

# Function to retrieve the file system structure
def get_file_system(local_folder):
    file_system = {}

    for root, dirs, files in os.walk(local_folder):
        if root == local_folder:
            file_system[root] = dirs + files
        else:
            # Calculate the relative path from the local_folder
            relative_path = os.path.relpath(root, local_folder)
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

# Navigate to the local folder where the repository was cloned
local_folder = "local_repo"  # Change this to your local folder name

# Get the file system structure
file_system_structure = get_file_system(local_folder)

# Convert the file system structure to JSON
file_system_json = json.dumps(file_system_structure, indent=4)

# Print or save the JSON as needed
print(file_system_json)
```
- **Main File Identification:** Utilize StableCode to identify main files and components based on the README content and file system structure.
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("stabilityai/stablecode-instruct-alpha-3b")
model = AutoModelForCausalLM.from_pretrained(
  "stabilityai/stablecode-instruct-alpha-3b",
  trust_remote_code=True,
  torch_dtype="auto",
)
model.cuda()
###### MODIFY THIS
inputs = tokenizer("###Instruction\nIdentify the main files of this app\n", return_tensors="pt").to("cuda")
######
tokens = model.generate(
  **inputs,
  max_new_tokens=48,
  temperature=0.2,
  do_sample=True,
)
print(tokenizer.decode(tokens[0], skip_special_tokens=True))
```
- **Generate Reverse engineering report:**
Provide the code of the main files to StableCode for review and analysis

- **User-Friendly Interface:** An intuitive web-based interface makes it easy to interact with the tool.

## Usage

1. Enter the GitHub repository URL you want to reverse engineer.
2. The tool will clone the repository to your local machine and provide you with reverse engineering report


## Getting Started

1. Clone this repository to your local machine.

   ```bash
   git clone https://github.com/your-username/StableReverse.git

