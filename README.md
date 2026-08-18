# swat4hcls.github.io

Source for SWAT4HCLS, migrated off the 18-year-old WordPress install at
[swat4ls.org](https://www.swat4ls.org). Past editions (2008–2026) and the blog
archive stay on swat4ls.org — pages here link back to it, not duplicate it.

## Two tiers

The site is split by what actually changes year to year:

- **General (repo root)** — the community, not any one edition: home, the live
  Proceedings archive, Vacancies, Who-is-who, and the person-centric author
  pages. None of this is Basel-specific and none of it should need touching
  when the conference moves to its next host city.
- **Edition-specific (`2027/`)** — everything about *this* conference: dates,
  programme, CFP, registration, biohackathon, sponsorship, local organizing
  committee. The next edition gets its own folder (e.g. `2028/`) rather than
  overwriting this one; old editions' folders can stay as an archive here or
  simply keep linking to swat4ls.org.

Plain HTML/CSS, no build step. GitHub Pages serves the repo root directly.

```
index.html                   General home (SWAT4HCLS, all editions)
proceedings.html              Live query against dblp's public SPARQL endpoint
author.html                   Per-author page, ?pid=<dblp pid> (e.g. author.html?pid=09/2013)
vacancies.html                 Aggregated job postings + "available for hire" listings
who-is-who.html               Central + local organizing committees, live contributor list
assets/css/style.css
assets/images/
assets/data/authors.jsonld    Extended author profiles (JSON-LD)
assets/data/posts.jsonld      Author announcements + vacancy listings (JSON-LD)
.github/ISSUE_TEMPLATE/        Submission forms: author-profile, author-post, company-vacancy
.github/workflows/             One workflow per form; each opens a PR, never auto-merges
.github/scripts/               Python parsers the workflows run (stdlib only, no deps)

2027/index.html                Basel 2027 edition home
2027/programme.html            Day-by-day schedule
2027/tutorials.html             \_ tutorials sub-page
2027/keynotes.html               \_ keynote speakers sub-page
2027/accepted-submissions.html    \_ accepted papers/posters/demos sub-page
2027/faq.html
2027/call-for-papers.html
2027/registration.html
2027/biohackathon.html
2027/sponsorship.html          Edition-specific pricing/contact
2027/organization.html         Local (Basel) organizing committee — central committee lives on who-is-who.html
```

`assets/` stays shared at the repo root; edition pages reference it as
`../assets/...`. A handful of old flat paths (`programme.html`, `faq.html`,
etc.) are kept as tiny meta-refresh redirect stubs into `2027/` — the site
briefly had those live at the root before this split, so incoming links don't
just 404.

### Adding a new edition

Copy the whole `2027/` folder to e.g. `2028/`, update its content, and repoint
the general pages' "Basel 2027 →" nav links / homepage CTA at the new folder.
Old editions can either stay in the repo as an archive or get pruned in favor
of the swat4ls.org archive — not yet decided.

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
   `conf/swat4ls` stream (same pattern as `proceedings.html`), also asking dblp
   for `dblp:orcid` on that PID — many dblp records already link an ORCID iD,
   independently of anything submitted to this site.
3. If an ORCID iD turns up (from dblp, or failing that from the submitted
   profile's `sameAs`), fetches `https://pub.orcid.org/v3.0/<id>/works` (public,
   no auth, CORS-open) and renders a "Recent publications" section — the
   person's broader output, not limited to SWAT4HCLS/dblp. No ORCID on either
   side, no section; nothing is invented.
4. If an ORCID iD turned up, also fetches `.../employments` for their current
   employer name and queries CORDIS (`POST https://cordis.europa.eu/datalab/sparql-api`,
   form-encoded `query` param, CORS-open) for EURIO organisations whose
   `legalName` contains a distinctive word from that employer name, with a
   project count per match — rendered as "EU-funded projects via CORDIS."
   This is **name-based matching, not an identifier join** — EURIO models
   organisations, not individual researchers, and an org's CORDIS legal name
   can differ completely from its common English name (e.g. Leiden University
   Medical Center is registered as "ACADEMISCH ZIEKENHUIS LEIDEN"). Generic
   words (university, medical, center, foundation, ...) are filtered out of
   the search terms so the query doesn't just match everything; results are
   still leads to verify, not confirmed affiliations — the page says so.
5. Renders whichever of the two it finds: dblp alone gives a working page
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
duplicated across pages by design (kept in sync manually; there are only 16
real pages total, plus 10 tiny redirect stubs for old flat URLs). When adding a page, copy the closest existing one **in the same
tier** (general vs. edition — they have different nav sets, see "Two tiers"
above) and update the `nav`/`subnav` `active` class and the `<title>`.

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
