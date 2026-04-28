import hashlib
import os
import re
import yaml


def expand_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


def parse_skill_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    metadata = {}
    body = text

    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            try:
                metadata = yaml.safe_load(text[3:end]) or {}
            except:
                metadata = {}
            body = text[end + 3 :]

    sections = {}
    current = "overview"
    sections[current] = ""

    for line in body.splitlines():
        m = re.match(r"^(##|###)\\s+(.*)", line)
        if m:
            current = m.group(2).strip().lower().replace(" ", "_")
            sections[current] = ""
        else:
            sections[current] += line + "\n"

    return {
        "metadata": metadata,
        "sections": sections,
        "body": body,
    }
