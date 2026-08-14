#!/usr/bin/env python3
"""Parse an "Author profile submission" issue form body and update
assets/data/authors.jsonld accordingly. Run by
.github/workflows/author-profile.yml — see README.md#author-pages.
"""
import json
import os
import re
import urllib.error
import urllib.request

from issue_form import fail, parse_body, slugify

REPO_ROOT = os.environ.get("GITHUB_WORKSPACE", ".")
ISSUE_BODY = os.environ["ISSUE_BODY"]

FIELD_MAP = {
    "dblp profile URL": "dblp",
    "Full name": "name",
    "ORCID iD": "orcid",
    "Affiliation": "affiliation",
    "Short bio": "bio",
    "Website / homepage URL": "homepage",
    "Photo": "photo",
}


def download_photo(photo_field, slug):
    if not photo_field:
        return None

    md_image = re.search(r"!\[[^\]]*\]\((https?://[^\s)]+)\)", photo_field)
    url = md_image.group(1) if md_image else None
    if not url:
        bare = photo_field.strip()
        if re.match(r"^https?://\S+$", bare):
            url = bare
    if not url:
        print(f"::warning::Could not find an image URL in the Photo field: {photo_field!r}")
        return None

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "swat4hcls-author-bot"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
            data = resp.read()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"::warning::Could not download photo from {url}: {e}")
        return None

    ext = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
    }.get(content_type)
    if not ext:
        m = re.search(r"\.(jpg|jpeg|png|webp|gif)(?:\?|$)", url, re.IGNORECASE)
        ext = m.group(1).lower() if m else None
    if not ext:
        print(f"::warning::Unrecognized image type ({content_type!r}) for {url}, skipping photo")
        return None

    images_dir = os.path.join(REPO_ROOT, "assets", "images", "authors")
    os.makedirs(images_dir, exist_ok=True)
    filename = f"{slug}.{ext}"
    with open(os.path.join(images_dir, filename), "wb") as f:
        f.write(data)
    print(f"Downloaded photo -> assets/images/authors/{filename}")
    return f"assets/images/authors/{filename}"


def main():
    raw = parse_body(ISSUE_BODY)
    data = {key: raw.get(label, "").strip() for label, key in FIELD_MAP.items()}

    m = re.match(r"^https?://dblp\.org/pid/(.+?)/?$", data["dblp"])
    if not m:
        fail(
            "The dblp profile URL must look like https://dblp.org/pid/XX/XXXX "
            f"(got: {data['dblp']!r}). Not processed automatically — see README.md#author-pages."
        )
    pid_path = m.group(1)
    full_pid = f"https://dblp.org/pid/{pid_path}"

    if not data["name"]:
        fail("Missing required field: Full name")

    slug = slugify(data["name"])
    depiction = download_photo(data.get("photo", ""), slug)

    node = {"@id": full_pid, "@type": "foaf:Person", "name": data["name"]}
    if data["orcid"]:
        orcid = data["orcid"]
        if not orcid.startswith("http"):
            orcid = f"https://orcid.org/{orcid}"
        node["sameAs"] = orcid
    if data["affiliation"]:
        node["affiliation"] = data["affiliation"]
    if data["bio"]:
        node["description"] = data["bio"]
    if data["homepage"]:
        node["homepage"] = data["homepage"]
    if depiction:
        node["depiction"] = depiction

    authors_path = os.path.join(REPO_ROOT, "assets", "data", "authors.jsonld")
    with open(authors_path) as f:
        doc = json.load(f)

    graph = doc.setdefault("@graph", [])
    existing = next((i for i, n in enumerate(graph) if n.get("@id") == full_pid), None)
    if existing is not None:
        graph[existing] = {**graph[existing], **node}
        action = "Update"
    else:
        graph.append(node)
        action = "Add"

    with open(authors_path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"slug={slug}\n")
            f.write(f"pid_path={pid_path}\n")
            f.write(f"name={data['name']}\n")
            f.write(f"action={action}\n")

    past_tense = "Added" if action == "Add" else "Updated"
    print(f"{past_tense} profile for {data['name']} ({full_pid})")


if __name__ == "__main__":
    main()
