# Capstone Project
## Files

* ```data/SGJobData.csv.xz```, this file is the CSV file data source for the project, except compressed so that GitHub can accept it.
* ```uat/sgjobdata.ipynb```, jupyter notebook for testing out graphs and commands etc.
* ```app.py```, main source code for streamlit application hosting

## How to set up environment
uv is a Python environment manager. To set up the environment, run the following commands after you have installed uv:

1. ```uv venv .venv``` : this will setup the virtual environment
2. ```uv venv .venv --python 3.12``` : this sets up the venv with python 3.12
3. ```source .venv/bin/activate``` : this activates the venv
4. ```uv pip install``` : this needs the uv.lock file, it installs everything needed for this environment

## How to Lock env and dependencies:
1. create a pyproject.toml file
2. run: ```uv lock```
