import os
import subprocess

def setup_project(project_path: str) -> None:
    """Set up a new project folder with git initialized."""
    if not os.path.exists(project_path):
        os.makedirs(project_path)
        print(f"Created project directory: {project_path}")
    else:
        print(f"Project directory already exists: {project_path}")

    try:
        subprocess.run(["git", "init"], cwd=project_path, check=True)
        print(f"Initialized git repository in: {project_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error initializing git repository: {e}")

def run(args: dict) -> str:
    name = args.get("name", "unknown")
    project_path = os.path.join(os.path.expanduser("~/Documents"), name)
    setup_project(project_path)
    return f"Created a new project folder at: {name}"
