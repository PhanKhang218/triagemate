"""Loader for modular agent skills stored as SKILL.md files under skills/."""

from __future__ import annotations

import os
import re

_SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")


def load_skill(name: str) -> str:
    """Return the markdown body of skills/<name>/SKILL.md with frontmatter stripped."""
    path = os.path.join(_SKILLS_DIR, name, "SKILL.md")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # Strip a leading YAML frontmatter block (--- ... ---).
    body = re.sub(r"^---.*?---\s*", "", content, count=1, flags=re.DOTALL)
    return body.strip()
