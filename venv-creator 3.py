import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import venv
import subprocess
import os
import sys
from pathlib import Path

DEFAULT_GITIGNORE = """
*.py[cod]
__pycache__/
*.so
.Python
.env
.venv/
env/
venv/
ENV/
.idea/
.vscode/
*.sublime-workspace
*.sublime-project
.DS_Store
"""

DEFAULT_README = """# {project_name}

## Description
Add your project description here.

## Setup
1. Create virtual environment: `python -m venv .venv`
2. Activate virtual environment: 
   - Windows: `.venv\\Scripts\\activate`
   - Unix/MacOS: `source .venv/bin/activate`
3. Install dependencies: `poetry install`

## Development
Add development instructions here.

## Testing
`pytest tests/`

## License
Add license information here.
"""

DEFAULT_PYPROJECT = """
[tool.poetry]
name = "{project_name}"
version = "0.1.0"
description = ""
authors = [""]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^23.0.0"
flake8 = "^6.0.0"
mypy = "^1.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

class ProjectCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Python Project Creator")
        self.root.geometry("700x600")
        
        self.project_templates = {
            "Modern Python Project": {
                "description": "Modern Python project structure with best practices",
                "structure": {
                    ".github": ["workflows", "PULL_REQUEST_TEMPLATE.md"],
                    "src": {
                        "core": ["__init__.py"],
                        "api": ["__init__.py"],
                        "services": ["__init__.py"],
                        "utils": ["__init__.py"],
                        "__init__.py": None
                    },
                    "tests": {
                        "core": ["__init__.py", "test_core.py"],
                        "api": ["__init__.py"],
                        "services": ["__init__.py"],
                        "utils": ["__init__.py"],
                        "conftest.py": None
                    },
                    "docs": {
                        "project_management": [
                            "requirements",
                            "architecture",
                            "decisions",
                            "deliverables"
                        ],
                        "technical": []
                    },
                    "scripts": ["setup.sh", "deploy.sh"],
                    "config": ["development.yaml", "production.yaml"],
                }
            },
            "Full Stack Project": {
                "description": "Full stack project with frontend and backend separation",
                "structure": {
                    "backend": {
                        "src": {
                            "core": ["__init__.py"],
                            "api": ["__init__.py"],
                            "services": ["__init__.py"],
                            "utils": ["__init__.py"],
                            "__init__.py": None
                        },
                        "tests": ["__init__.py"],
                        "config": []
                    },
                    "frontend": {
                        "src": ["components", "services", "utils", "assets"],
                        "public": [],
                        "tests": []
                    },
                    "docs": {
                        "project_management": [
                            "requirements",
                            "architecture",
                            "decisions",
                            "deliverables"
                        ],
                        "technical": ["api", "deployment"]
                    },
                    ".github": ["workflows"]
                }
            }
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # Project name
        tk.Label(self.root, text="Project Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(fill=tk.X, padx=5)
        
        # Directory selection
        tk.Label(self.root, text="Project Location:").pack(pady=5)
        self.dir_frame = tk.Frame(self.root)
        self.dir_frame.pack(fill=tk.X, padx=5)
        
        self.dir_entry = tk.Entry(self.dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(self.dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT)
        
        # Requirements file selection
        tk.Label(self.root, text="Requirements File (optional):").pack(pady=5)
        self.req_frame = tk.Frame(self.root)
        self.req_frame.pack(fill=tk.X, padx=5)
        
        self.req_entry = tk.Entry(self.req_frame)
        self.req_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(self.req_frame, text="Browse", command=self.browse_requirements).pack(side=tk.RIGHT)
        
        # Project template selection
        tk.Label(self.root, text="Project Template:").pack(pady=5)
        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(self.root, textvariable=self.template_var)
        self.template_dropdown['values'] = list(self.project_templates.keys())
        self.template_dropdown.pack(pady=5)
        self.template_dropdown.bind('<<ComboboxSelected>>', self.on_template_select)
        
        # Description label
        self.desc_label = tk.Label(self.root, text="", wraplength=500)
        self.desc_label.pack(pady=5)
        
        # Additional options
        self.options_frame = ttk.LabelFrame(self.root, text="Additional Options")
        self.options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_poetry = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.options_frame, text="Use Poetry for dependency management", 
                       variable=self.use_poetry).pack(anchor=tk.W)
        
        self.add_docker = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.options_frame, text="Add Docker configuration", 
                       variable=self.add_docker).pack(anchor=tk.W)
        
        self.add_github_actions = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.options_frame, text="Add GitHub Actions workflow", 
                       variable=self.add_github_actions).pack(anchor=tk.W)
        
        # Create button
        tk.Button(self.root, text="Create Project", command=self.create_project).pack(pady=20)
    
    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir_path)
    
    def browse_requirements(self):
        req_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if req_path:
            self.req_entry.delete(0, tk.END)
            self.req_entry.insert(0, req_path)
    
    def on_template_select(self, event=None):
        template = self.template_var.get()
        if template in self.project_templates:
            self.desc_label.config(text=self.project_templates[template]['description'])
    
    def create_directory_structure(self, base_path, structure):
        for name, contents in structure.items():
            path = os.path.join(base_path, name)
            
            if contents is None:
                # Create empty file
                Path(path).touch()
            else:
                os.makedirs(path, exist_ok=True)
                
                if isinstance(contents, list):
                    for item in contents:
                        if '.' in item:  # If item is a file
                            Path(os.path.join(path, item)).touch()
                        else:  # If item is a directory
                            os.makedirs(os.path.join(path, item), exist_ok=True)
                elif isinstance(contents, dict):
                    self.create_directory_structure(path, contents)
    
    def create_project(self):
        project_name = self.name_entry.get()
        base_dir = self.dir_entry.get()
        template = self.template_var.get()
        
        if not all([project_name, base_dir, template]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            # Create project directory
            project_path = os.path.join(base_dir, project_name)
            os.makedirs(project_path, exist_ok=True)
            
            # Create virtual environment
            venv.create(os.path.join(project_path, '.venv'), with_pip=True)
            
            # Create project structure
            self.create_directory_structure(project_path, 
                                         self.project_templates[template]['structure'])
            
            # Create essential files
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write(DEFAULT_GITIGNORE)
            
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(DEFAULT_README.format(project_name=project_name))
            
            if self.use_poetry.get():
                with open(os.path.join(project_path, 'pyproject.toml'), 'w') as f:
                    f.write(DEFAULT_PYPROJECT.format(project_name=project_name))
            
            if self.add_docker.get():
                with open(os.path.join(project_path, 'Dockerfile'), 'w') as f:
                    f.write(f"FROM python:3.9-slim\nWORKDIR /app\nCOPY . .\nRUN pip install poetry && poetry install\nCMD ['poetry', 'run', 'python', '-m', '{project_name}']")
            
            if self.add_github_actions.get():
                workflow_dir = os.path.join(project_path, '.github', 'workflows')
                os.makedirs(workflow_dir, exist_ok=True)
                with open(os.path.join(workflow_dir, 'ci.yml'), 'w') as f:
                    f.write("""name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install poetry
        poetry install
    - name: Run tests
      run: poetry run pytest
""")
            
            # Install requirements if specified
            req_path = self.req_entry.get()
            if req_path:
                pip_path = os.path.join(project_path, '.venv', 'Scripts' if sys.platform == 'win32' else 'bin', 'pip')
                subprocess.run([pip_path, 'install', '-r', req_path])
            
            messagebox.showinfo("Success", "Project created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectCreatorGUI(root)
    root.mainloop()
