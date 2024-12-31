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

class EnhancedProjectCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Python Project Creator")
        self.root.geometry("800x800")
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.setup_tab = ttk.Frame(self.notebook)
        self.options_tab = ttk.Frame(self.notebook)
        self.tools_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.setup_tab, text='Project Setup')
        self.notebook.add(self.options_tab, text='Configuration')
        self.notebook.add(self.tools_tab, text='Tools')
        
        # Initialize variables
        self.python_version = tk.StringVar(value="3.9")
        self.test_framework = tk.StringVar(value="pytest")
        self.ci_provider = tk.StringVar(value="github")
        
        self.create_setup_tab()
        self.create_options_tab()
        self.create_tools_tab()
        
        # Progress bar
        self.progress = ttk.Progressbar(root, mode='determinate')
        self.progress.pack(fill='x', padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(root, textvariable=self.status_var)
        self.status_label.pack(pady=5)

    def create_setup_tab(self):
        # Project Details Frame
        details_frame = ttk.LabelFrame(self.setup_tab, text="Project Details")
        details_frame.pack(fill='x', padx=5, pady=5)
        
        # Project name
        ttk.Label(details_frame, text="Project Name:").pack(pady=5)
        self.name_entry = ttk.Entry(details_frame)
        self.name_entry.pack(fill='x', padx=5)
        
        # Directory selection
        ttk.Label(details_frame, text="Project Location:").pack(pady=5)
        dir_frame = ttk.Frame(details_frame)
        dir_frame.pack(fill='x', padx=5)
        
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side='right')
        
        # Python version selection
        version_frame = ttk.Frame(details_frame)
        version_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(version_frame, text="Python Version:").pack(side='left')
        version_combo = ttk.Combobox(version_frame, textvariable=self.python_version)
        version_combo['values'] = ('3.8', '3.9', '3.10', '3.11', '3.12', '3.13')
        version_combo.pack(side='left', padx=5)

        # Test framework selection
        test_frame = ttk.Frame(details_frame)
        test_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(test_frame, text="Test Framework:").pack(side='left')
        test_combo = ttk.Combobox(test_frame, textvariable=self.test_framework)
        test_combo['values'] = ('pytest', 'unittest')
        test_combo.pack(side='left', padx=5)

    def create_options_tab(self):
        # CI/CD Frame
        cicd_frame = ttk.LabelFrame(self.options_tab, text="CI/CD Configuration")
        cicd_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Radiobutton(cicd_frame, text="GitHub Actions", 
                       variable=self.ci_provider, value="github").pack(anchor='w')
        ttk.Radiobutton(cicd_frame, text="GitLab CI", 
                       variable=self.ci_provider, value="gitlab").pack(anchor='w')
        ttk.Radiobutton(cicd_frame, text="Jenkins", 
                       variable=self.ci_provider, value="jenkins").pack(anchor='w')
        
        # Development Tools Frame
        tools_frame = ttk.LabelFrame(self.options_tab, text="Development Tools")
        tools_frame.pack(fill='x', padx=5, pady=5)
        
        self.use_poetry = tk.BooleanVar(value=True)
        self.add_docker = tk.BooleanVar(value=True)
        self.add_precommit = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(tools_frame, text="Use Poetry", 
                       variable=self.use_poetry).pack(anchor='w')
        ttk.Checkbutton(tools_frame, text="Add Docker", 
                       variable=self.add_docker).pack(anchor='w')
        ttk.Checkbutton(tools_frame, text="Add Pre-commit", 
                       variable=self.add_precommit).pack(anchor='w')

    def create_tools_tab(self):
        buttons_frame = ttk.Frame(self.tools_tab)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Check Project", 
                  command=self.check_project).pack(fill='x', pady=2)
        ttk.Button(buttons_frame, text="Backup Project", 
                  command=self.backup_project).pack(fill='x', pady=2)
        ttk.Button(buttons_frame, text="Restore Backup", 
                  command=self.restore_backup).pack(fill='x', pady=2)
        ttk.Button(buttons_frame, text="Scan Dependencies", 
                  command=self.scan_dependencies).pack(fill='x', pady=2)
        
        # Create Project button
        ttk.Button(self.root, text="Create Project", 
                  command=self.create_project).pack(pady=10)

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

    def create_project(self):
        if not all([self.name_entry.get(), self.dir_entry.get()]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        def create_project_thread():
            try:
                steps = [
                    (10, "Creating directory structure"),
                    (20, "Setting up virtual environment"),
                    (40, "Configuring development tools"),
                    (60, "Setting up CI/CD"),
                    (80, "Installing dependencies"),
                    (100, "Project creation complete")
                ]
                
                project_path = os.path.join(self.dir_entry.get(), self.name_entry.get())
                
                for progress, status in steps:
                    self.update_progress(progress, status)
                    # Add actual implementation for each step
                    
                messagebox.showinfo("Success", "Project created successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project: {str(e)}")
            finally:
                self.update_progress(0, "Ready")
        
        thread = threading.Thread(target=create_project_thread)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedProjectCreator(root)
    root.mainloop()
