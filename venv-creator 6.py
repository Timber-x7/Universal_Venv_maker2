import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import venv
import subprocess
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import threading
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
def setup_logging():
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'venv_creator.log')
        
        # Create handlers
        file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
        console_handler = logging.StreamHandler()
        
        # Create formatters and add it to handlers
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        file_handler.setFormatter(logging.Formatter(log_format))
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Get the logger
        logger = logging.getLogger('VenvCreator')
        logger.setLevel(logging.DEBUG)
        
        # Remove any existing handlers
        logger.handlers = []
        
        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    except Exception as e:
        print(f"Failed to setup logging: {str(e)}")
        return logging.getLogger('VenvCreator')

# Initialize logger
logger = setup_logging()

class EnhancedProjectCreator:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("Universal Python Project Creator")
            self.root.geometry("800x800")
            
            # Store base directory
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
            logger.info(f"Base directory: {self.base_dir}")
            
            # Load file structures from text files
            self.load_file_structures()
            
            # Load project categories and templates
            self.load_templates()
            
            # Create main notebook for tabs
            self.notebook = ttk.Notebook(root)
            self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
            
            # Create tabs
            self.setup_tab = ttk.Frame(self.notebook)
            self.options_tab = ttk.Frame(self.notebook)
            self.tools_tab = ttk.Frame(self.notebook)
            self.templates_tab = ttk.Frame(self.notebook)
            self.structure_tab = ttk.Frame(self.notebook)
            
            self.notebook.add(self.setup_tab, text='Project Setup')
            self.notebook.add(self.options_tab, text='Configuration')
            self.notebook.add(self.tools_tab, text='Tools')
            self.notebook.add(self.templates_tab, text='Templates')
            self.notebook.add(self.structure_tab, text='Structure')
            
            # Initialize variables
            self.python_version = tk.StringVar(value="3.9")
            self.test_framework = tk.StringVar(value="pytest")
            self.ci_provider = tk.StringVar(value="github")
            self.template_var = tk.StringVar()
            self.category_var = tk.StringVar()
            self.structure_var = tk.StringVar(value="Software Development")
            self.use_poetry = tk.BooleanVar(value=True)
            self.add_docker = tk.BooleanVar(value=False)
            
            self.create_setup_tab()
            self.create_options_tab()
            self.create_tools_tab()
            self.create_templates_tab()
            self.create_structure_tab()
            
            # Progress bar
            self.progress = ttk.Progressbar(root, mode='determinate')
            self.progress.pack(fill='x', padx=5, pady=5)
            
            # Status label
            self.status_var = tk.StringVar(value="Ready")
            self.status_label = ttk.Label(root, textvariable=self.status_var)
            self.status_label.pack(pady=5)
            
            # Create Project button
            tk.Button(root, text="Create Project", command=self.create_project).pack(pady=10)
            
            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to initialize application: {str(e)}")

    def load_file_structures(self):
        try:
            # Load structure from Software Dev.txt
            with open(os.path.join(self.base_dir, "Software Dev.txt"), 'r') as f:
                software_dev_structure = self.parse_structure(f.read())

            # Load structure from Project Manager.txt
            with open(os.path.join(self.base_dir, "Project Manager.txt"), 'r') as f:
                project_manager_structure = self.parse_structure(f.read())

            # Load structure from Project_DevMan.txt
            with open(os.path.join(self.base_dir, "Project_DevMan.txt"), 'r') as f:
                dev_man_structure = self.parse_structure(f.read())

            self.file_structures = {
                "Software Development": {
                    "description": "Standard software development project structure",
                    "structure": software_dev_structure
                },
                "Project Management": {
                    "description": "Project management directory structure",
                    "structure": project_manager_structure
                },
                "Development with PM": {
                    "description": "Combined software development and project management structure",
                    "structure": dev_man_structure
                }
            }
            logger.info("File structures loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load file structures: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to load file structures: {str(e)}")

    def parse_structure(self, content):
        structure = {}
        current_path = []
        
        for line in content.split('\n'):
            if not line.strip() or line.endswith('/'):  # Skip empty lines and root directory
                continue
                
            # Count the depth by the number of leading spaces/tabs
            depth = 0
            line_stripped = line.lstrip()
            if '├──' in line or '└──' in line:
                depth = (len(line) - len(line_stripped)) // 2
                name = line_stripped.replace('├── ', '').replace('└── ', '').strip()
            else:
                continue
            
            # Adjust current path based on depth
            while len(current_path) > depth:
                current_path.pop()
            
            if depth == len(current_path):
                current_path.append(name)
            
            # Build the nested structure
            current_dict = structure
            for path_part in current_path[:-1]:
                if path_part not in current_dict:
                    current_dict[path_part] = {}
                current_dict = current_dict[path_part]
            
            if current_path:
                if current_path[-1] not in current_dict:
                    current_dict[current_path[-1]] = {}
        
        return structure

    def load_templates(self):
        # Project categories from v1
        self.categories = {
            "AI & ML": {
                "description": "Projects related to artificial intelligence and machine learning",
                "templates": ["basic_ml", "nlp_project"]
            },
            "Office doc types": {
                "description": "Tools for working with office documents",
                "templates": ["word_automation", "excel_reporting"]
            },
            "Utilities": {
                "description": "General purpose utility scripts",
                "templates": ["file_manager", "web_scraper"]
            }
        }
        
        # Project templates from v2-v5
        self.project_templates = {
            "Modern Python Project": {
                "description": "Modern Python project structure with best practices",
                "structure": {
                    ".github": {
                        "workflows": [],
                        "ISSUE_TEMPLATE": ["bug_report.md", "feature_request.md"],
                        "PULL_REQUEST_TEMPLATE.md": None
                    },
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
            },
            "Project Management": {
                "description": "Project management directory structure",
                "structure": {
                    "01_Initiation": [],
                    "02_Planning": [],
                    "03_Execution": [],
                    "04_Monitoring_and_Control": [],
                    "05_Closing": [],
                    "Documents": ["Contracts", "Reports", "Meeting_Minutes"],
                    "Financials": [],
                    "Communication": [],
                    "Risk_Management": [],
                    "Stakeholder_Management": []
                }
            }
        }

    def create_setup_tab(self):
        # Project Details Frame
        details_frame = ttk.LabelFrame(self.setup_tab, text="Project Details")
        details_frame.pack(fill='x', padx=5, pady=5)
        
        # Project name
        tk.Label(self.setup_tab, text="Project Name:").pack(pady=5)
        self.name_entry = tk.Entry(self.setup_tab)
        self.name_entry.pack(fill=tk.X, padx=5)
        
        # Directory selection
        tk.Label(self.setup_tab, text="Project Location:").pack(pady=5)
        dir_frame = ttk.Frame(self.setup_tab)
        dir_frame.pack(fill=tk.X, padx=5)
        
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT)
        
        # Python version selection
        version_frame = ttk.Frame(self.setup_tab)
        version_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(version_frame, text="Python Version:").pack(side=tk.LEFT)
        version_combo = ttk.Combobox(version_frame, textvariable=self.python_version)
        version_combo['values'] = ('3.8', '3.9', '3.10', '3.11', '3.12')
        version_combo.pack(side=tk.LEFT, padx=5)

        # Requirements file selection
        tk.Label(self.setup_tab, text="Requirements File (optional):").pack(pady=5)
        req_frame = ttk.Frame(self.setup_tab)
        req_frame.pack(fill=tk.X, padx=5)
        
        self.req_entry = ttk.Entry(req_frame)
        self.req_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(req_frame, text="Browse", command=self.browse_requirements).pack(side=tk.RIGHT)

    def create_options_tab(self):
        # Development tools frame
        tools_frame = ttk.LabelFrame(self.options_tab, text="Development Tools")
        tools_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.use_poetry = tk.BooleanVar(value=True)
        self.add_docker = tk.BooleanVar(value=True)
        self.add_precommit = tk.BooleanVar(value=True)
        self.add_devcontainer = tk.BooleanVar(value=True)
        self.add_makefile = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(tools_frame, text="Use Poetry", variable=self.use_poetry).pack(anchor=tk.W)
        ttk.Checkbutton(tools_frame, text="Add Docker", variable=self.add_docker).pack(anchor=tk.W)
        ttk.Checkbutton(tools_frame, text="Add Pre-commit", variable=self.add_precommit).pack(anchor=tk.W)
        ttk.Checkbutton(tools_frame, text="Add Dev Container", variable=self.add_devcontainer).pack(anchor=tk.W)
        ttk.Checkbutton(tools_frame, text="Add Makefile", variable=self.add_makefile).pack(anchor=tk.W)
        
        # CI/CD frame
        cicd_frame = ttk.LabelFrame(self.options_tab, text="CI/CD Configuration")
        cicd_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Radiobutton(cicd_frame, text="GitHub Actions", variable=self.ci_provider, value="github").pack(anchor=tk.W)
        ttk.Radiobutton(cicd_frame, text="GitLab CI", variable=self.ci_provider, value="gitlab").pack(anchor=tk.W)
        ttk.Radiobutton(cicd_frame, text="Jenkins", variable=self.ci_provider, value="jenkins").pack(anchor=tk.W)

    def create_tools_tab(self):
        buttons_frame = ttk.Frame(self.tools_tab)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Check Project", command=self.check_project).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Backup Project", command=self.backup_project).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Restore Backup", command=self.restore_backup).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Scan Dependencies", command=self.scan_dependencies).pack(fill=tk.X, pady=2)

    def create_templates_tab(self):
        # Category selection
        tk.Label(self.templates_tab, text="Project Category:").pack(pady=5)
        self.category_dropdown = ttk.Combobox(self.templates_tab, textvariable=self.category_var)
        self.category_dropdown['values'] = list(self.categories.keys())
        self.category_dropdown.pack(pady=5)
        self.category_dropdown.bind('<<ComboboxSelected>>', self.on_category_select)
        
        # Template selection
        tk.Label(self.templates_tab, text="Project Template:").pack(pady=5)
        self.template_dropdown = ttk.Combobox(self.templates_tab, textvariable=self.template_var)
        self.template_dropdown['values'] = list(self.project_templates.keys())
        self.template_dropdown.pack(pady=5)
        self.template_dropdown.bind('<<ComboboxSelected>>', self.on_template_select)
        
        # Description label
        self.desc_label = tk.Label(self.templates_tab, text="", wraplength=500)
        self.desc_label.pack(pady=5)

    def create_structure_tab(self):
        # Structure selection
        tk.Label(self.structure_tab, text="Project Structure:").pack(pady=5)
        structure_frame = ttk.Frame(self.structure_tab)
        structure_frame.pack(fill='x', padx=5, pady=5)
        
        for structure in self.file_structures.keys():
            ttk.Radiobutton(structure_frame, text=structure, 
                          variable=self.structure_var, 
                          value=structure,
                          command=self.on_structure_select).pack(anchor=tk.W)
        
        # Description label
        self.structure_desc_label = tk.Label(self.structure_tab, text="", wraplength=500)
        self.structure_desc_label.pack(pady=5)
        
        # Structure preview (using a text widget)
        tk.Label(self.structure_tab, text="Structure Preview:").pack(pady=5)
        preview_frame = ttk.Frame(self.structure_tab)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbars first
        y_scrollbar = ttk.Scrollbar(preview_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Then add text widget
        self.structure_preview = tk.Text(preview_frame, height=15, wrap=tk.NONE,
                                       yscrollcommand=y_scrollbar.set,
                                       xscrollcommand=x_scrollbar.set)
        self.structure_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.structure_preview.yview)
        x_scrollbar.config(command=self.structure_preview.xview)
        
        # Make text widget read-only
        self.structure_preview.config(state=tk.DISABLED)
        
        # Show initial structure
        self.on_structure_select()
        
        logger.debug("Structure tab created successfully")

    def on_category_select(self, event=None):
        category = self.category_var.get()
        if category in self.categories:
            self.template_dropdown['values'] = self.categories[category]['templates']
            self.desc_label.config(text=self.categories[category]['description'])

    def on_template_select(self, event=None):
        template = self.template_var.get()
        if template in self.project_templates:
            self.desc_label.config(text=self.project_templates[template]['description'])

    def on_structure_select(self, event=None):
        structure = self.structure_var.get()
        if structure in self.file_structures:
            # Update description
            self.structure_desc_label.config(text=self.file_structures[structure]['description'])
            
            # Generate structure preview
            preview_text = self.generate_structure_preview(structure)
            
            # Update preview text
            self.structure_preview.config(state=tk.NORMAL)
            self.structure_preview.delete('1.0', tk.END)
            self.structure_preview.insert('1.0', preview_text)
            self.structure_preview.config(state=tk.DISABLED)
            
            logger.debug(f"Structure selected: {structure}")
            logger.debug(f"Preview text: {preview_text}")

    def generate_structure_preview(self, structure_name):
        def _generate_tree(structure, prefix=""):
            lines = []
            items = list(structure.items())
            
            for i, (name, contents) in enumerate(items):
                is_last = i == len(items) - 1
                lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")
                
                if isinstance(contents, dict):
                    extension = "    " if is_last else "│   "
                    lines.extend(_generate_tree(contents, prefix + extension))
            
            return lines
        
        try:
            structure = self.file_structures[structure_name]['structure']
            tree_lines = _generate_tree(structure)
            preview = "\n".join(tree_lines)
            logger.debug(f"Generated preview for {structure_name}:\n{preview}")
            return preview
        except Exception as e:
            error_msg = f"Failed to generate preview: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def create_directory_structure(self, base_path, structure):
        for name, contents in structure.items():
            path = os.path.join(base_path, name)
            
            if contents is None:
                # Create empty file
                Path(path).touch()
            elif isinstance(contents, list):
                # Create directory and its contents
                os.makedirs(path, exist_ok=True)
                for item in contents:
                    if '.' in item:  # It's a file
                        Path(os.path.join(path, item)).touch()
                    else:  # It's a directory
                        os.makedirs(os.path.join(path, item), exist_ok=True)
            elif isinstance(contents, dict):
                # Create directory and recurse
                os.makedirs(path, exist_ok=True)
                self.create_directory_structure(path, contents)

    def create_configuration_files(self, project_path):
        # Create configuration files based on options
        if self.add_precommit.get():
            with open(os.path.join(project_path, '.pre-commit-config.yaml'), 'w') as f:
                f.write(DEFAULT_PRECOMMIT)
                
        if self.add_devcontainer.get():
            devcontainer_dir = os.path.join(project_path, '.devcontainer')
            os.makedirs(devcontainer_dir, exist_ok=True)
            with open(os.path.join(devcontainer_dir, 'devcontainer.json'), 'w') as f:
                f.write(DEFAULT_DEVCONTAINER)
                
        if self.add_makefile.get():
            with open(os.path.join(project_path, 'Makefile'), 'w') as f:
                f.write(DEFAULT_MAKEFILE)
        
        # Create common configuration files
        config_files = {
            '.editorconfig': DEFAULT_EDITORCONFIG,
            'SECURITY.md': DEFAULT_SECURITY,
            'CONTRIBUTING.md': DEFAULT_CONTRIBUTING,
            '.github/dependabot.yml': DEFAULT_DEPENDABOT,
            '.github/ISSUE_TEMPLATE/bug_report.md': DEFAULT_ISSUE_TEMPLATE
        }
        
        for path, content in config_files.items():
            full_path = os.path.join(project_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

    def update_progress(self, value, status):
        self.progress['value'] = value
        self.status_var.set(status)
        self.root.update_idletasks()

    def check_project(self):
        project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Project directory does not exist")
            return
            
        checks = [
            ("Virtual environment", os.path.exists(os.path.join(project_path, '.venv'))),
            ("Git repository", os.path.exists(os.path.join(project_path, '.git'))),
            ("Project structure", os.path.exists(os.path.join(project_path, 'src'))),
            ("Tests directory", os.path.exists(os.path.join(project_path, 'tests'))),
        ]
        
        report = "\n".join([f"✓ {name}" if status else f"✗ {name}" for name, status in checks])
        messagebox.showinfo("Project Check Results", report)

    def backup_project(self):
        project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Project directory does not exist")
            return
            
        backup_name = f"{self.name_entry.get()}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(self.dir_entry.get(), backup_name)
        
        try:
            shutil.copytree(project_path, backup_path)
            messagebox.showinfo("Success", f"Backup created at: {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {str(e)}")

    def restore_backup(self):
        backup_path = filedialog.askdirectory(title="Select Backup Directory")
        if not backup_path:
            return
            
        project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
        
        try:
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            shutil.copytree(backup_path, project_path)
            messagebox.showinfo("Success", "Project restored from backup")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restore backup: {str(e)}")

    def scan_dependencies(self):
        project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Project directory does not exist")
            return
            
        try:
            if self.use_poetry.get():
                result = subprocess.run(['poetry', 'show', '--outdated'], 
                                     cwd=project_path, capture_output=True, text=True)
                messagebox.showinfo("Dependency Scan Results", result.stdout or "All dependencies up to date")
            else:
                messagebox.showinfo("Info", "Dependency scanning requires Poetry")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan dependencies: {str(e)}")

    def create_ci_config(self):
        config_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
        
        if self.ci_provider.get() == "github":
            workflow_dir = os.path.join(config_path, '.github', 'workflows')
            os.makedirs(workflow_dir, exist_ok=True)
            with open(os.path.join(workflow_dir, 'ci.yml'), 'w') as f:
                f.write(self.get_github_workflow())
        elif self.ci_provider.get() == "gitlab":
            with open(os.path.join(config_path, '.gitlab-ci.yml'), 'w') as f:
                f.write(self.get_gitlab_config())
        elif self.ci_provider.get() == "jenkins":
            with open(os.path.join(config_path, 'Jenkinsfile'), 'w') as f:
                f.write(self.get_jenkins_config())

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def browse_requirements(self):
        req_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if req_path:
            self.req_entry.delete(0, tk.END)
            self.req_entry.insert(0, req_path)

    def get_github_workflow(self):
        return f"""name: Python CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python {self.python_version.get()}
      uses: actions/setup-python@v4
      with:
        python-version: {self.python_version.get()}
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install
    - name: Run tests
      run: poetry run {self.test_framework.get()}
"""

    def get_gitlab_config(self):
        return f"""image: python:{self.python_version.get()}

before_script:
  - pip install poetry
  - poetry install

test:
  script:
    - poetry run {self.test_framework.get()}
"""

    def get_jenkins_config(self):
        return f"""pipeline {{
    agent {{ docker {{ image 'python:{self.python_version.get()}' }} }}
    
    stages {{
        stage('Build') {{
            steps {{
                sh 'pip install poetry'
                sh 'poetry install'
            }}
        }}
        stage('Test') {{
            steps {{
                sh 'poetry run {self.test_framework.get()}'
            }}
        }}
    }}
}}"""

    def setup_poetry(self, project_path):
        try:
            # Check if poetry is installed
            try:
                subprocess.run(['poetry', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Poetry not found, installing...")
                # Install poetry using pip
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'poetry'], check=True)
            
            logger.debug("Initializing poetry project")
            subprocess.run(['poetry', 'init',
                          '--name', self.name_entry.get(),
                          '--description', 'A Python project',
                          '--author', 'Author Name',
                          '--python', f'^{self.python_version.get()}',
                          '--dependency', self.test_framework.get(),
                          '--dev-dependency', 'black',
                          '--dev-dependency', 'flake8',
                          '--no-interaction'],
                          cwd=project_path,
                          check=True)
            
            # Install dependencies
            logger.debug("Installing poetry dependencies")
            subprocess.run(['poetry', 'install'], cwd=project_path, check=True)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Poetry command failed: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to setup poetry: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def setup_docker(self, project_path):
        dockerfile = f"""FROM python:{self.python_version.get()}
WORKDIR /app
COPY . /app/
RUN pip install poetry && poetry install
CMD ["poetry", "run", "python", "src/main.py"]
"""
        with open(os.path.join(project_path, 'Dockerfile'), 'w') as f:
            f.write(dockerfile)

    def setup_precommit(self, project_path):
        config = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
-   repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
    -   id: black
-   repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
    -   id: flake8
"""
        with open(os.path.join(project_path, '.pre-commit-config.yaml'), 'w') as f:
            f.write(config)
        subprocess.run(['pre-commit', 'install'], cwd=project_path)

    def create_project(self):
        if not all([self.name_entry.get(), self.dir_entry.get()]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        thread = threading.Thread(target=self.create_project_thread)
        thread.start()

    def create_project_thread(self):
        try:
            logger.info("Starting project creation")
            project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
            
            # Step 1: Create directory structure (10%)
            self.update_progress(10, "Creating directory structure")
            logger.info("Creating directory structure")
            os.makedirs(project_path, exist_ok=True)
            
            # Create structure based on selected structure
            structure = self.structure_var.get()
            if structure in self.file_structures:
                logger.info(f"Using structure template: {structure}")
                self.create_directory_structure(project_path, self.file_structures[structure]['structure'])
            else:
                logger.warning("No structure template selected, using basic structure")
                # Create basic structure if no structure selected
                os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
                os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)
                os.makedirs(os.path.join(project_path, 'docs'), exist_ok=True)
            
            # Step 2: Set up virtual environment (20%)
            self.update_progress(20, "Setting up virtual environment")
            logger.info("Setting up virtual environment")
            venv.create(os.path.join(project_path, '.venv'), with_pip=True)
            
            # Step 3: Initialize git (30%)
            self.update_progress(30, "Initializing git repository")
            logger.info("Initializing git repository")
            subprocess.run(['git', 'init'], cwd=project_path)
            
            # Create .gitignore
            logger.debug("Creating .gitignore")
            gitignore = """__pycache__/
*.py[cod]
*$py.class
.venv/
.env
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
logs/
"""
            with open(os.path.join(project_path, '.gitignore'), 'w') as f:
                f.write(gitignore)
            
            # Step 4: Configure development tools (60%)
            self.update_progress(60, "Configuring development tools")
            logger.info("Configuring development tools")
            if self.use_poetry.get():
                logger.debug("Setting up Poetry")
                self.setup_poetry(project_path)
            if self.add_docker.get():
                logger.debug("Setting up Docker")
                self.setup_docker(project_path)
            
            # Create configuration files
            logger.debug("Creating configuration files")
            self.create_configuration_files(project_path)
            
            # Step 5: Set up CI/CD (80%)
            self.update_progress(80, "Setting up CI/CD")
            logger.info("Setting up CI/CD")
            if self.ci_provider.get() == "github":
                logger.debug("Configuring GitHub Actions")
                workflow_dir = os.path.join(project_path, '.github', 'workflows')
                os.makedirs(workflow_dir, exist_ok=True)
                with open(os.path.join(workflow_dir, 'ci.yml'), 'w') as f:
                    f.write(self.get_github_workflow())
            elif self.ci_provider.get() == "gitlab":
                logger.debug("Configuring GitLab CI")
                with open(os.path.join(project_path, '.gitlab-ci.yml'), 'w') as f:
                    f.write(self.get_gitlab_config())
            elif self.ci_provider.get() == "jenkins":
                logger.debug("Configuring Jenkins")
                with open(os.path.join(project_path, 'Jenkinsfile'), 'w') as f:
                    f.write(self.get_jenkins_config())
            
            # Install requirements if specified
            req_path = self.req_entry.get()
            if req_path:
                logger.info(f"Installing requirements from: {req_path}")
                pip_path = os.path.join(project_path, '.venv', 'Scripts' if sys.platform == 'win32' else 'bin', 'pip')
                subprocess.run([pip_path, 'install', '-r', req_path])
            
            # Create README.md
            logger.debug("Creating README.md")
            readme = f"""# {self.name_entry.get()}

A Python project created with Universal Python Project Creator.

## Structure
This project uses the {self.structure_var.get()} structure template.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   poetry install
   ```

## Development

- Run tests: `poetry run {self.test_framework.get()}`
- Format code: `poetry run black .`
- Lint code: `poetry run flake8`
"""
            with open(os.path.join(project_path, 'README.md'), 'w') as f:
                f.write(readme)
            
            # Create example source and test files
            logger.debug("Creating example source and test files")
            with open(os.path.join(project_path, 'src', '__init__.py'), 'w') as f:
                f.write('')
            
            with open(os.path.join(project_path, 'src', 'main.py'), 'w') as f:
                f.write('''def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
            
            with open(os.path.join(project_path, 'tests', 'test_main.py'), 'w') as f:
                f.write('''from src.main import main

def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\\n"
''')
            
            # Step 6: Complete (100%)
            self.update_progress(100, "Project creation complete")
            logger.info("Project created successfully")
            messagebox.showinfo("Success", "Project created successfully!")
            
        except Exception as e:
            error_msg = f"Failed to create project: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("Error", error_msg)
        finally:
            self.update_progress(0, "Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedProjectCreator(root)
    root.mainloop()
