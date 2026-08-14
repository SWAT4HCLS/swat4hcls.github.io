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
assets/css/style.css
assets/images/
assets/data/authors.jsonld    Extended author profiles (JSON-LD), admin-curated
.github/ISSUE_TEMPLATE/author-profile.yml   Submission form for author profiles
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

### Adding a profile

Authors request an addition via the **"Author profile submission"** GitHub issue
template (`.github/ISSUE_TEMPLATE/author-profile.yml`), which asks for their dblp
profile URL (to identify the PID), name, ORCID, affiliation, bio, homepage, and a
photo URL. An admin verifies the dblp link, then adds/updates one node in
`assets/data/authors.jsonld`:

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
own PID URI) but needs no library to read — `author.html` just does
`fetch().then(r => r.json())` and treats `@graph` as an array. Commit and push;
no build step.

**Not yet built:** self-service editing via ORCID login. That needs a small
backend (OAuth token exchange + authenticated writes to this repo) that a static
GitHub Pages site can't provide alone — out of scope until that's stood up
separately. For now all edits go through the issue-review flow above.

## Editing content

Every page is standalone HTML — no templating. The nav, sidebar, and footer are
duplicated across pages by design (kept in sync manually; there are only 12 pages).
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
