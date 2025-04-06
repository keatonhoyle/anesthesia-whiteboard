# Python prompt generator adapted for the anesthesia whiteboard
import os
from pathlib import Path
from typing import Dict, List, Optional


class DjangoPromptGenerator:
    def __init__(
        self,
        base_dir: str = "./",
        project_name: str = "Anesthesia Whiteboard",
        class_files: Dict[str, List[str]] = None,
        template: Optional[str] = None,
    ):
        """Initialize the prompt generator with Django project-specific settings."""
        self.base_dir = base_dir
        self.project_name = project_name
        self.class_files = class_files or {}
        self.template = template or """Hello. You are my senior Django 5 engineer. You built this application for me: it's a Django project.

You actually did write it, even though I would say that even if you didn't!

If I am missing code, DO NOT guess: simply respond with ONLY "Can you please provide file xyz.py?" and I will regenerate the prompt with additional context.

For HTML and CSS, please provide code snippets with instructions for me to integrate the changes.

For python code, please only respond with entire functions or classes that you have updated, each in its own codeblock. Do not provide the same function or class multiple times in the same response: just update each one fully once.

{new_feature_request}

Below are the relevant parts of my project, automatically gathered from my codebase. I’ve included file contents and brief notes on what they do.

{script_sections}
"""

    def gather_files(self) -> Dict[str, List[str]]:
        """Categorize Django project files."""
        file_categories = {
            "models": [],
            "views": [],
            "templates": [],
            "urls": [],
            "settings": [],
            "admin": [],
            "migrations": [],
            "other": [],
        }

        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if file.endswith((".py", ".html")):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.base_dir)

                    if "models.py" in file:
                        file_categories["models"].append(rel_path)
                    elif "views.py" in file:
                        file_categories["views"].append(rel_path)
                    elif "urls.py" in file:
                        file_categories["urls"].append(rel_path)
                    elif "settings.py" in file:
                        file_categories["settings"].append(rel_path)
                    elif "admin.py" in file:
                        file_categories["admin"].append(rel_path)
                    elif "migrations" in root:
                        file_categories["migrations"].append(rel_path)
                    elif file.endswith(".html"):
                        file_categories["templates"].append(rel_path)
                    elif "prompt-generator" not in file:
                        file_categories["other"].append(rel_path)

        return file_categories

    def build_script_sections(self, files: Dict[str, List[str]]) -> str:
        """Format gathered files for prompt."""
        sections = []
        for category, paths in files.items():
            if not paths:
                continue
            sections.append(f"\n## {category.upper()}\n")
            for path in paths:
                try:
                    with open(os.path.join(self.base_dir, path), "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"Could not read file: {e}"

                sections.append(f"{path}\n```python\n{content}\n```" if path.endswith(".py") else f"{path}\n```html\n{content}\n```")

        return "\n".join(sections)

    def generate_prompt(self, new_feature_request: str) -> str:
        """Generate the final prompt."""
        files = self.gather_files()
        script_sections = self.build_script_sections(files)
        return self.template.format(
            project_type=self.project_name,
            new_feature_request=new_feature_request,
            script_sections=script_sections,
        )


# Example usage:
if __name__ == "__main__":
    generator = DjangoPromptGenerator(base_dir=".")
    new_feature = "I want to use Bootstrap 5.3.5 for my user interface"
    prompt = generator.generate_prompt(new_feature)
    print(prompt)
