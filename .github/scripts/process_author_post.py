#!/usr/bin/env python3
"""Parse an "Author page announcement" issue form body, verify the
submitter's dblp pid already has a profile in authors.jsonld, and append
a post to assets/data/posts.jsonld. Run by
.github/workflows/author-post.yml — see README.md#author-pages.
"""
import datetime
import json
import os
import re

from issue_form import fail, parse_body, slugify

REPO_ROOT = os.environ.get("GITHUB_WORKSPACE", ".")
ISSUE_BODY = os.environ["ISSUE_BODY"]
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]

FIELD_MAP = {
    "Your dblp profile URL": "dblp",
    "Post type": "type",
    "Headline": "headline",
    "Details": "text",
    "Link": "url",
    "Show until (YYYY-MM-DD)": "validThrough",
}

TYPE_MAP = {
    "Job posting": ("job-posting", "schema:JobPosting"),
    "Looking for work": ("looking-for-work", "schema:SocialMediaPosting"),
    "Announcement": ("announcement", "schema:SocialMediaPosting"),
    "Work update": ("work-update", "schema:SocialMediaPosting"),
}


def main():
    raw = parse_body(ISSUE_BODY)
    data = {key: raw.get(label, "").strip() for label, key in FIELD_MAP.items()}

    m = re.match(r"^https?://dblp\.org/pid/(.+?)/?$", data["dblp"])
    if not m:
        fail(
            "The dblp profile URL must look like https://dblp.org/pid/XX/XXXX "
            f"(got: {data['dblp']!r})."
        )
    full_pid = f"https://dblp.org/pid/{m.group(1)}"

    authors_path = os.path.join(REPO_ROOT, "assets", "data", "authors.jsonld")
    with open(authors_path) as f:
        authors_doc = json.load(f)
    profile = next((n for n in authors_doc.get("@graph", []) if n.get("@id") == full_pid), None)
    if profile is None:
        fail(
            f"No existing author profile found for {full_pid}. "
            "Submit an \"Author profile submission\" issue first — see README.md#author-pages."
        )

    if not data["headline"] or not data["text"]:
        fail("Headline and Details are both required.")

    if data["validThrough"]:
        try:
            datetime.date.fromisoformat(data["validThrough"])
        except ValueError:
            fail(f"'Show until' must be YYYY-MM-DD (got: {data['validThrough']!r}).")

    post_type_slug, schema_type = TYPE_MAP.get(data["type"], ("announcement", "schema:SocialMediaPosting"))

    posts_path = os.path.join(REPO_ROOT, "assets", "data", "posts.jsonld")
    with open(posts_path) as f:
        posts_doc = json.load(f)
    graph = posts_doc.setdefault("@graph", [])

    post_id = f"{full_pid}#post-{slugify(data['headline'])}-{ISSUE_NUMBER}"
    node = {
        "@id": post_id,
        "@type": schema_type,
        "author": full_pid,
        "headline": data["headline"],
        "text": data["text"],
        "datePosted": datetime.date.today().isoformat(),
        "postType": post_type_slug,
    }
    if data["url"]:
        node["url"] = data["url"]
    if data["validThrough"]:
        node["validThrough"] = data["validThrough"]

    graph.append(node)

    with open(posts_path, "w") as f:
        json.dump(posts_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"author_name={profile.get('name', full_pid)}\n")
            f.write(f"headline={data['headline']}\n")
            f.write(f"slug={slugify(data['headline'])}\n")

    print(f"Added post {post_id!r} for {profile.get('name', full_pid)}")


if __name__ == "__main__":
    main()
