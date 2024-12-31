import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import venv
import subprocess
import os
import sys
from pathlib import Path

class VenvCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Environment Creator")
        self.root.geometry("600x500")
        
        self.project_templates = {
            "Software Development": {
                "description": "Standard software development project structure",
                "structure": {
                    "src": ["components", "services", "utils", "assets"],
                    "tests": [],
                    "docs": [],
                    "config": [],
                    "build": [],
                    "public": []
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
            },
            "Development with PM": {
                "description": "Combined software development and project management structure",
                "structure": {
                    "Project_Management": {
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
                    },
                    "Software_Development": {
                        "src": ["components", "services", "utils", "assets"],
                        "tests": [],
                        "docs": [],
                        "config": [],
                        "build": [],
                        "public": []
                    }
                }
            }
        }
        
        # Save templates to JSON if doesn't exist
        if not os.path.exists('project_templates.json'):
            with open('project_templates.json', 'w') as f:
                json.dump(self.project_templates, f, indent=4)
        
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
            os.makedirs(path, exist_ok=True)
            
            if isinstance(contents, list):
                for subdir in contents:
                    os.makedirs(os.path.join(path, subdir), exist_ok=True)
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
            venv.create(os.path.join(project_path, 'venv'), with_pip=True)
            
            # Create project structure
            self.create_directory_structure(project_path, self.project_templates[template]['structure'])
            
            # Create empty main.py
            with open(os.path.join(project_path, 'main.py'), 'w') as f:
                pass
            
            # Install requirements if specified
            req_path = self.req_entry.get()
            if req_path:
                pip_path = os.path.join(project_path, 'venv', 'Scripts' if sys.platform == 'win32' else 'bin', 'pip')
                subprocess.run([pip_path, 'install', '-r', req_path])
            
            messagebox.showinfo("Success", "Project created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VenvCreatorGUI(root)
    root.mainloop()
