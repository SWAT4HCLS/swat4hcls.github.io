#!/usr/bin/env python3
"""Parse a "Company vacancy listing" issue form body and append a
JobPosting to assets/data/posts.jsonld. Unlike author submissions, this
one is NOT auto-verified against anything — payment/sponsorship status
is confirmed by an admin out of band before the generated PR is merged.
Run by .github/workflows/company-vacancy.yml — see README.md#author-pages.
"""
import datetime
import json
import os

from issue_form import fail, parse_body, slugify

REPO_ROOT = os.environ.get("GITHUB_WORKSPACE", ".")
ISSUE_BODY = os.environ["ISSUE_BODY"]
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]

FIELD_MAP = {
    "Company / organization name": "company",
    "Company website": "companyUrl",
    "Job title / headline": "headline",
    "Details": "text",
    "Application link": "applyUrl",
    "Show until (YYYY-MM-DD)": "validThrough",
}


def main():
    raw = parse_body(ISSUE_BODY)
    data = {key: raw.get(label, "").strip() for label, key in FIELD_MAP.items()}

    if not data["company"] or not data["headline"] or not data["text"]:
        fail("Company name, job title, and details are all required.")

    if data["validThrough"]:
        try:
            datetime.date.fromisoformat(data["validThrough"])
        except ValueError:
            fail(f"'Show until' must be YYYY-MM-DD (got: {data['validThrough']!r}).")

    posts_path = os.path.join(REPO_ROOT, "assets", "data", "posts.jsonld")
    with open(posts_path) as f:
        posts_doc = json.load(f)
    graph = posts_doc.setdefault("@graph", [])

    slug = slugify(data["headline"])
    post_id = f"urn:swat4hcls:vacancy:{slugify(data['company'])}-{slug}-{ISSUE_NUMBER}"
    hiring_org = {"@type": "schema:Organization", "name": data["company"]}
    if data["companyUrl"]:
        hiring_org["url"] = data["companyUrl"]

    node = {
        "@id": post_id,
        "@type": "schema:JobPosting",
        "hiringOrganization": hiring_org,
        "headline": data["headline"],
        "text": data["text"],
        "datePosted": datetime.date.today().isoformat(),
        "postType": "job-posting",
    }
    if data["applyUrl"]:
        node["url"] = data["applyUrl"]
    if data["validThrough"]:
        node["validThrough"] = data["validThrough"]

    graph.append(node)

    with open(posts_path, "w") as f:
        json.dump(posts_doc, f, indent=2, ensure_ascii=False)
        f.write("\n")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"company={data['company']}\n")
            f.write(f"headline={data['headline']}\n")
            f.write(f"slug={slug}\n")

    print(f"Added company vacancy {post_id!r} for {data['company']} (UNVERIFIED — admin must confirm payment before merging)")


if __name__ == "__main__":
    main()
