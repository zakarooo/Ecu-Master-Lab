#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=========================================================
ECU MASTER LAB - Project Tree Analyzer
Version : 1.0
Auteur  : ChatGPT
=========================================================
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache"
}

IGNORED_FILES = {
    ".DS_Store"
}


class TreeAnalyzer:

    def __init__(self, root):
        self.root = Path(root).resolve()

        self.total_files = 0
        self.total_dirs = 0
        self.total_size = 0

        self.extensions = {}

        self.tree = []

        self.files = []

    #########################################################

    def readable_size(self, size):

        units = ["B", "KB", "MB", "GB"]

        index = 0

        while size >= 1024 and index < len(units)-1:
            size /= 1024
            index += 1

        return f"{size:.2f} {units[index]}"

    #########################################################

    def sha256(self, filename):

        try:

            h = hashlib.sha256()

            with open(filename, "rb") as f:

                while True:

                    data = f.read(8192)

                    if not data:
                        break

                    h.update(data)

            return h.hexdigest()

        except:

            return ""

    #########################################################

    def scan(self):

        self.walk(self.root)

    #########################################################

    def walk(self, folder):

        entries = sorted(folder.iterdir(), key=lambda x: x.name.lower())

        for entry in entries:

            if entry.name in IGNORED_FILES:
                continue

            if entry.is_dir():

                if entry.name in IGNORED_DIRS:
                    continue

                self.total_dirs += 1

                self.tree.append({
                    "type": "directory",
                    "path": str(entry.relative_to(self.root))
                })

                self.walk(entry)

            else:

                self.total_files += 1

                size = entry.stat().st_size

                self.total_size += size

                ext = entry.suffix.lower()

                if ext == "":
                    ext = "NO_EXTENSION"

                self.extensions[ext] = self.extensions.get(ext, 0) + 1

                file_info = {
                    "path": str(entry.relative_to(self.root)),
                    "name": entry.name,
                    "extension": ext,
                    "size": size,
                    "size_readable": self.readable_size(size),
                    "sha256": self.sha256(entry)
                }

                self.files.append(file_info)

                self.tree.append({
                    "type": "file",
                    "path": file_info["path"]
                })

    #########################################################

    def print_summary(self):

        print("=" * 60)
        print(" ECU MASTER LAB - TREE ANALYZER")
        print("=" * 60)

        print()

        print("Projet :", self.root)

        print()

        print("Dossiers :", self.total_dirs)
        print("Fichiers :", self.total_files)
        print("Taille   :", self.readable_size(self.total_size))

        print()

        print("Extensions")

        for ext in sorted(self.extensions):

            print(f" {ext:15} {self.extensions[ext]}")

    #########################################################

    def save_tree(self):

        output = self.root / "audit"

        output.mkdir(exist_ok=True)

        txt = output / "project_tree.txt"

        with open(txt, "w", encoding="utf8") as f:

            for item in self.tree:

                if item["type"] == "directory":
                    f.write("[DIR ] ")

                else:
                    f.write("[FILE] ")

                f.write(item["path"])
                f.write("\n")

        print("✓", txt)

    #########################################################

    def save_json(self):

        output = self.root / "audit"

        output.mkdir(exist_ok=True)

        report = {

            "date": datetime.now().isoformat(),

            "project": str(self.root),

            "summary": {

                "directories": self.total_dirs,

                "files": self.total_files,

                "size": self.total_size,

                "size_readable": self.readable_size(
                    self.total_size
                )

            },

            "extensions": self.extensions,

            "files": self.files

        }

        filename = output / "tree_report.json"

        with open(filename, "w", encoding="utf8") as f:

            json.dump(report, f, indent=4)

        print("✓", filename)

    #########################################################

    def save_markdown(self):

        output = self.root / "audit"

        output.mkdir(exist_ok=True)

        filename = output / "tree_report.md"

        with open(filename, "w", encoding="utf8") as f:

            f.write("# ECU MASTER LAB\n\n")

            f.write("## Résumé\n\n")

            f.write(f"- Dossiers : {self.total_dirs}\n")
            f.write(f"- Fichiers : {self.total_files}\n")
            f.write(f"- Taille : {self.readable_size(self.total_size)}\n\n")

            f.write("## Extensions\n\n")

            for ext in sorted(self.extensions):

                f.write(f"- {ext} : {self.extensions[ext]}\n")

            f.write("\n")

            f.write("## Fichiers\n\n")

            for file in self.files:

                f.write(
                    f"- {file['path']} ({file['size_readable']})\n"
                )

        print("✓", filename)

    #########################################################

    def save_html(self):

        output = self.root / "audit"

        output.mkdir(exist_ok=True)

        filename = output / "tree_report.html"

        html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ECU MASTER LAB</title>

<style>

body{{font-family:Arial;margin:40px;background:#fafafa}}

table{{border-collapse:collapse;width:100%}}

td,th{{border:1px solid #ccc;padding:6px}}

th{{background:#222;color:white}}

</style>

</head>

<body>

<h1>ECU MASTER LAB</h1>

<h2>Résumé</h2>

<ul>

<li>Dossiers : {self.total_dirs}</li>

<li>Fichiers : {self.total_files}</li>

<li>Taille : {self.readable_size(self.total_size)}</li>

</ul>

<h2>Liste des fichiers</h2>

<table>

<tr>

<th>Nom</th>

<th>Extension</th>

<th>Taille</th>

</tr>

"""

        for file in self.files:

            html += f"""

<tr>

<td>{file['path']}</td>

<td>{file['extension']}</td>

<td>{file['size_readable']}</td>

</tr>

"""

        html += """

</table>

</body>

</html>

"""

        with open(filename, "w", encoding="utf8") as f:

            f.write(html)

        print("✓", filename)


############################################################


def main():

    analyzer = TreeAnalyzer(".")

    analyzer.scan()

    analyzer.print_summary()

    analyzer.save_tree()

    analyzer.save_json()

    analyzer.save_markdown()

    analyzer.save_html()


############################################################

if __name__ == "__main__":

    main()