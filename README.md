# swat4hcls.github.io

Source for the current SWAT4HCLS conference edition (Basel 2027), migrated off the
18-year-old WordPress install at [swat4ls.org](https://www.swat4ls.org).

This repo holds only the **current edition**. Past editions (2008–2026), proceedings,
and the blog archive stay on swat4ls.org — every page here links back to it.

## Structure

Plain HTML/CSS, no build step. GitHub Pages serves the repo root directly.

```
index.html                   Home
programme.html                Programme overview (day-by-day schedule)
tutorials.html                 \_ tutorials sub-page
keynotes.html                   \_ keynote speakers sub-page
accepted-submissions.html        \_ accepted papers/posters/demos sub-page
faq.html
call-for-papers.html
registration.html
biohackathon.html
sponsorship.html
organization.html
proceedings.html              Live query against dblp's public SPARQL endpoint
author.html                   Per-author page, ?pid=<dblp pid> (e.g. author.html?pid=09/2013)
vacancies.html                 Aggregated job postings + "available for hire" listings
assets/css/style.css
assets/images/
assets/data/authors.jsonld    Extended author profiles (JSON-LD)
assets/data/posts.jsonld      Author announcements + vacancy listings (JSON-LD)
.github/ISSUE_TEMPLATE/        Submission forms: author-profile, author-post, company-vacancy
.github/workflows/             One workflow per form; each opens a PR, never auto-merges
.github/scripts/               Python parsers the workflows run (stdlib only, no deps)
```

`programme.html`, `tutorials.html`, `keynotes.html`, and `accepted-submissions.html`
share a small sub-nav and are meant to be edited as a group.

## Proceedings page

`proceedings.html` does not store paper data. It runs a SPARQL query against
`https://sparql.dblp.org/sparql` in the visitor's browser at load time, against
dblp's `conf/swat4ls` stream, and renders the results grouped by year. Nothing to
update by hand when new papers get indexed by dblp.

## Author pages

`author.html?pid=<dblp pid>` (e.g. `author.html?pid=09/2013`) is a single template
for every author, not a page per person. On load it:

1. Fetches `assets/data/authors.jsonld` and looks for a node whose `@id` matches
   the full dblp PID URI (`https://dblp.org/pid/<pid>`).
2. Runs a live SPARQL query for that PID's papers and co-authors in the
   `conf/swat4ls` stream (same pattern as `proceedings.html`).
3. Renders whichever of the two it finds: dblp alone gives a working page
   (papers, co-authors, dblp link) with no submitted profile; a matching
   `authors.jsonld` node adds a photo, bio, affiliation, homepage, and ORCID.

Every author name on `proceedings.html` (paper lists and the contributor chips)
links to `author.html?pid=...`, whether or not that person has submitted a profile.

### Adding a profile (automated)

Authors submit the **"Author profile submission"** issue form (dblp profile URL,
name, ORCID, affiliation, bio, homepage, photo). Opening the issue triggers
`.github/workflows/author-profile.yml`, which:

1. Runs `.github/scripts/process_author_issue.py` to parse the form, validate the
   dblp URL is in the required `https://dblp.org/pid/XX/XXXX` form, download the
   photo (plain URL or a dragged-in GitHub-hosted image, either works), and
   upsert one node into `assets/data/authors.jsonld`.
2. Commits that to a new branch and opens a **pull request** — it never pushes
   straight to `main`.
3. If parsing fails (bad URL, missing required field), it comments on the issue
   explaining why instead of opening a PR.

An admin reviews the PR diff and merges. That's the actual approval step — there's
no login, so review is what stops anyone editing someone else's profile.

```json
{
  "@id": "https://dblp.org/pid/09/2013",
  "@type": "foaf:Person",
  "name": "Marco Roos",
  "sameAs": "https://orcid.org/0000-0000-0000-0000",
  "affiliation": "Leiden University Medical Center",
  "description": "Short bio text.",
  "homepage": "https://example.org/~roos",
  "depiction": "assets/images/authors/marco-roos.jpg"
}
```

The file is genuine JSON-LD (FOAF/schema.org/OWL vocabulary, `@id` reuses dblp's
own PID URI) but needs no library to read — pages just do
`fetch().then(r => r.json())` and treat `@graph` as an array.

**Not yet built:** self-service editing via ORCID login. That needs a small
backend (OAuth token exchange + authenticated writes to this repo) that a static
GitHub Pages site can't provide alone — out of scope until that's stood up
separately. For now all edits go through the issue → PR → merge flow above.

## Announcements and vacancies

`assets/data/posts.jsonld` holds two kinds of entries, both `schema.org`-typed:

- **Author posts** (`schema:SocialMediaPosting` with `author` = a dblp PID) —
  announcements, "looking for work," or job postings from anyone who already has
  an entry in `authors.jsonld`. Submitted via the **"Author page announcement"**
  form → `.github/workflows/author-post.yml` →
  `process_author_post.py`, which **refuses to create a post for a pid that has
  no existing profile** (fails the run and comments on the issue) — so someone
  has to be an approved author before they can post at all.
- **Company vacancies** (`schema:JobPosting` with `hiringOrganization` instead of
  `author`) — paid listings from organizations, not gated by dblp/proceedings.
  Submitted via **"Company vacancy listing"** → `.github/workflows/company-vacancy.yml`
  → `process_company_vacancy.py`. This one does **no verification at all** —
  payment or micro-sponsorship status isn't tracked anywhere in this repo, so the
  PR it opens is titled `⚠ UNPAID vacancy: ...` as a loud reminder. An admin
  confirms payment out of band (however that's actually arranged — bank
  transfer, invoice, GitHub Sponsors, whatever) before merging.

Both feed `author.html` (an author's own posts, filtered by their pid) and
`vacancies.html` (all non-expired `job-posting` and `looking-for-work` entries,
site-wide). Posts with a `validThrough` date in the past are hidden client-side,
not deleted — job listings and "looking for work" posts age out on their own.

All three workflows share the same shape: parse issue → validate → write JSON-LD
→ open a PR → **never auto-merge**. A human always reviews the diff before
anything goes live. If submission volume grows enough that this becomes a
bottleneck, the next step would be tightening what gets auto-merged (e.g. author
profile updates with a verified dblp match) rather than removing review
entirely — company vacancies in particular should probably always stay
human-gated given the money involved.

### One-time repo setting these workflows need

They push a branch and open a PR using the default `GITHUB_TOKEN`, which needs
**Settings → Actions → General → Workflow permissions → "Allow GitHub Actions to
create and approve pull requests"** enabled. Without it, `gh pr create` fails
silently from the workflow's point of view (the issue just never gets a PR) —
check that setting first if submissions stop producing PRs.

## Editing content

Every page is standalone HTML — no templating. The nav, sidebar, and footer are
duplicated across pages by design (kept in sync manually; there are only 14 pages).
When adding a page, copy the closest existing one and update the `nav`/`subnav`
`active` class and the `<title>`.

## Local preview

```bash
python3 -m http.server 8934
```

Then open `http://localhost:8934/`.

## Assets carried over from the old site

- `assets/images/skyline-basel2027.png` — cropped from the original WordPress
  header banner (`swat4ls-header-1-basel2027-2X.png`). Every edition since 2008
  has shipped its own host-city skyline illustration; keep that going for future
  editions by cropping the equivalent artwork the same way.
- `assets/images/icon-{mastodon,bluesky,youtube}.png` — social icons, unchanged.
