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
        self.root.title("Virtual Environment Creator")
        self.root.geometry("600x400")
        
        # Load project categories
        self.categories = self.load_categories()
        
        self.create_widgets()
        
    def load_categories(self):
        categories_json = {
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
        
        # Save categories to file if it doesn't exist
        if not os.path.exists('project_categories.json'):
            with open('project_categories.json', 'w') as f:
                json.dump(categories_json, f, indent=4)
        else:
            with open('project_categories.json', 'r') as f:
                categories_json = json.load(f)
                
        return categories_json
    
    def create_widgets(self):
        # Directory selection
        tk.Label(self.root, text="Project Directory:").pack(pady=5)
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
        
        # Project category selection
        tk.Label(self.root, text="Project Category:").pack(pady=5)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.root, textvariable=self.category_var)
        self.category_dropdown['values'] = list(self.categories.keys())
        self.category_dropdown.pack(pady=5)
        self.category_dropdown.bind('<<ComboboxSelected>>', self.on_category_select)
        
        # Template selection
        tk.Label(self.root, text="Template:").pack(pady=5)
        self.template_var = tk.StringVar()
        self.template_dropdown = ttk.Combobox(self.root, textvariable=self.template_var)
        self.template_dropdown.pack(pady=5)
        
        # Description label
        self.desc_label = tk.Label(self.root, text="", wraplength=500)
        self.desc_label.pack(pady=5)
        
        # Create button
        tk.Button(self.root, text="Create Virtual Environment", command=self.create_venv).pack(pady=20)
        
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
            
    def on_category_select(self, event=None):
        category = self.category_var.get()
        if category in self.categories:
            self.template_dropdown['values'] = self.categories[category]['templates']
            self.desc_label.config(text=self.categories[category]['description'])
            
    def create_venv(self):
        dir_path = self.dir_entry.get()
        if not dir_path:
            messagebox.showerror("Error", "Please select a directory")
            return
            
        try:
            # Create virtual environment
            venv.create(dir_path, with_pip=True)
            
            # Create empty Python file
            with open(os.path.join(dir_path, 'main.py'), 'w') as f:
                pass
            
            # Install requirements if specified
            req_path = self.req_entry.get()
            if req_path:
                pip_path = os.path.join(dir_path, 'Scripts' if sys.platform == 'win32' else 'bin', 'pip')
                subprocess.run([pip_path, 'install', '-r', req_path])
            
            messagebox.showinfo("Success", "Virtual environment created successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create virtual environment: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VenvCreatorGUI(root)
    root.mainloop()
