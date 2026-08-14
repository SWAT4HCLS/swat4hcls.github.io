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
assets/css/style.css
assets/images/
```

`programme.html`, `tutorials.html`, `keynotes.html`, and `accepted-submissions.html`
share a small sub-nav and are meant to be edited as a group.

## Proceedings page

`proceedings.html` does not store paper data. It runs a SPARQL query against
`https://sparql.dblp.org/sparql` in the visitor's browser at load time, against
dblp's `conf/swat4ls` stream, and renders the results grouped by year. Nothing to
update by hand when new papers get indexed by dblp.

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
