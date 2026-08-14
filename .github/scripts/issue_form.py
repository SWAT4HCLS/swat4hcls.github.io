"""Shared helpers for parsing GitHub Issue Form bodies.
Used by process_author_issue.py and process_author_post.py.
"""
import re
import sys


def parse_body(body):
    """GitHub renders Issue Forms as repeated '### Label\\n\\nvalue' blocks."""
    fields = {}
    for part in re.split(r"\n### ", "\n" + body.strip()):
        part = part.strip()
        if not part:
            continue
        header, _, rest = part.partition("\n")
        value = rest.strip()
        if value == "_No response_":
            value = ""
        fields[header.strip()] = value
    return fields


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "item"


def fail(message):
    print(f"::error::{message}")
    sys.exit(1)
