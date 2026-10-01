# ridenhourlab.org

Source for the Ridenhour Lab website, published with GitHub Pages.

## Updating the site

1. Edit the content:
   - **Publications:** `data/publications.json`. Add new papers at the top. Fields: `year`, `type` (`article` or `chapter`), `authors`, `title`, `venue`, `details` (volume:pages), `doi`, and `url` (usually `https://doi.org/` + the DOI). The `doi` field drives the Altmetric badge; add `preprint_doi` to show a second badge for a preprint version.
   - **Teaching:** `data/teaching.json`. Add a term to a course's `offerings`, and put the syllabus PDF in `syllabi/`. Set `current_term` to highlight the current semester.
   - **Page text:** `src/*.html`. The header and footer are in `src/_layout.html`.
   - **CV:** save it as `cv/Ridenhour-CV.pdf`. The CV buttons appear automatically.
   - **Photo:** save a square headshot as `assets/headshot.jpg` (about 600×600). It appears on the home page automatically.
2. Rebuild: `python3 build.py`
3. Publish: `git add -A && git commit -m "Update site" && git push`

GitHub Pages updates within a minute or two.

Don't edit the top-level `index.html`, `research.html`, `publications.html` or `teaching.html` directly, because `build.py` overwrites them. The `blog.html`, `twitter.html` and `contact.html` pages redirect old links to the home page.
