#!/usr/bin/env python3
"""Build the Ridenhour Lab website.

Edit the files in data/ (publications, teaching) or src/ (page text), then run:

    python3 build.py

This regenerates the .html pages in this folder. Commit and push to publish.
Only the Python standard library is needed.
"""
import html, json, os, re, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
NAV = [("index.html", "Home"), ("research.html", "Research"),
       ("publications.html", "Publications"), ("teaching.html", "Teaching")]
CV_PATH = "cv/Ridenhour-CV.pdf"
PHOTO_PATH = "assets/headshot.jpg"
ME = re.compile(r"(B\.\s?J\.\s?Ridenhour|Ridenhour,\s?B\.\s?J\.|Ridenhour, B\.(?!\s?J)|B\. Ridenhour)")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def exists(rel):
    return os.path.exists(os.path.join(ROOT, rel))


def pub_html(p):
    authors = ME.sub(r'<span class="me">\1</span>', html.escape(p["authors"], quote=False))
    title = p["title"].rstrip(".?") + ("?" if p["title"].endswith("?") else ".")
    venue = p["venue"]
    details = f" {p['details']}" if p.get("details") else ""
    venue_html = (f'{venue}{details}.' if venue.startswith("In ")
                  else f'<span class="venue">{venue}</span>{details}.')
    link = ""
    if p.get("url"):
        label = "DOI" if "doi.org/" in p["url"] else "Link"
        link = f'<a class="doi" href="{html.escape(p["url"])}">{label}</a>'
    tag = {"chapter": '<span class="tag">Chapter</span>',
           "preprint": '<span class="tag">Preprint</span>'}.get(p["type"], "")
    return (f'<li class="pub" data-type="{p["type"]}" data-year="{p["year"]}">'
            f'<div class="title">{title}{tag}</div>'
            f'<div class="meta"><span class="authors">{authors}</span>{"" if p["authors"].endswith(".") else "."} {p["year"]}. '
            f'{venue_html}{link}</div></li>')


def pub_list(pubs):
    return '<ul class="pubs">\n' + "\n".join(pub_html(p) for p in pubs) + "\n</ul>"


def all_pubs(pubs):
    groups = OrderedDict()
    for p in sorted(pubs, key=lambda p: -p["year"]):
        groups.setdefault(p["year"], []).append(p)
    return "\n".join(f'<section class="year-group"><h2>{y}</h2>\n{pub_list(ps)}\n</section>'
                     for y, ps in groups.items())


def courses_html(t):
    out = []
    for c in t["courses"]:
        former = f'<span class="formerly">formerly {c["formerly"]}</span>' if c.get("formerly") else ""
        terms = []
        for o in c["offerings"]:
            cls = ' class="now"' if o["term"] == t.get("current_term") else ""
            label = o["term"] + (" (current)" if cls else "")
            if o.get("syllabus"):
                if not exists(o["syllabus"]):
                    print(f"  warning: missing syllabus {o['syllabus']}", file=sys.stderr)
                terms.append(f'<li{cls}><a href="{o["syllabus"]}" title="Download syllabus (PDF)">{label}</a></li>')
            else:
                terms.append(f'<li{cls}><span>{label}</span></li>')
        out.append(f'<div class="course"><div class="code">{c["code"]}{former}</div>'
                   f'<div><div class="ctitle">{c["title"]}</div><ul class="terms">{"".join(terms)}</ul></div></div>')
    return "\n".join(out)


def table(rows, cols):
    head = "".join(f"<th>{h}</th>" for h, _ in cols)
    body = "".join("<tr>" + "".join(f"<td>{r.get(k, '')}</td>" for _, k in cols) + "</tr>" for r in rows)
    return f'<div class="table-scroll"><table class="simple"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def main():
    pubs = load("publications.json")
    teaching = load("teaching.json")
    by_url = {p["url"].lower(): p for p in pubs if p.get("url")}
    layout = open(os.path.join(SRC, "_layout.html"), encoding="utf-8").read()
    has_cv, has_photo = exists(CV_PATH), exists(PHOTO_PATH)

    for page, _ in NAV:
        src = open(os.path.join(SRC, page), encoding="utf-8").read()
        title = re.search(r"<!-- title: (.*?) -->", src).group(1)
        desc = re.search(r"<!-- description: (.*?) -->", src).group(1)
        body = re.sub(r"<!-- (title|description): .*? -->\n", "", src)

        def pubs_token(m):
            sel = []
            for doi in m.group(1).split("|"):
                hit = next((p for u, p in by_url.items() if doi.lower() in u), None)
                if hit: sel.append(hit)
                else: print(f"  warning: no publication matches {doi}", file=sys.stderr)
            return pub_list(sel)
        body = re.sub(r"\{\{PUBS:(.*?)\}\}", pubs_token, body)
        repl = {
            "RECENT_PUBS": pub_list(sorted(pubs, key=lambda p: -p["year"])[:5]),
            "ALL_PUBS": all_pubs(pubs),
            "PUB_COUNT": str(len(pubs)),
            "COURSES": courses_html(teaching),
            "MENTORED": table(teaching["mentored"], [("Course", "code"), ("Title", "title"), ("Terms", "terms")]),
            "EARLIER": table(teaching["earlier"], [("Course", "code"), ("Title", "title"), ("Institution", "where"), ("Terms", "terms")]),
            "CV_BUTTON": f'<li><a class="btn primary" href="{CV_PATH}">CV (PDF)</a></li>' if has_cv else "",
            "CV_LINK": f' A full list is also in my <a href="{CV_PATH}">CV (PDF)</a>.' if has_cv else "",
            "PHOTO": f'<img class="photo" src="{PHOTO_PATH}" alt="Ben Ridenhour" width="240" height="240">' if has_photo else "",
            "HERO_CLASS": " has-photo" if has_photo else "",
        }
        for k, v in repl.items():
            body = body.replace("{{" + k + "}}", v)

        cur = ' aria-current="page"'
        nav = "\n".join(
            '        <li><a href="%s"%s>%s</a></li>'
            % ("./" if href == "index.html" else href, cur if href == page else "", label)
            for href, label in NAV)
        scripts = '<script src="assets/pubs.js"></script>' if page == "publications.html" else ""
        out = (layout.replace("{{TITLE}}", html.escape(title)).replace("{{DESCRIPTION}}", html.escape(desc))
               .replace("{{PATH}}", "" if page == "index.html" else page).replace("{{NAV}}", nav)
               .replace("{{CONTENT}}", body.strip()).replace("{{SCRIPTS}}", scripts))
        left = re.findall(r"\{\{[A-Z_:]+", out)
        if left:
            print(f"  warning: unreplaced placeholders in {page}: {left}", file=sys.stderr)
        with open(os.path.join(ROOT, page), "w", encoding="utf-8") as f:
            f.write(out)
        print(f"built {page}")
    print(f"{len(pubs)} publications; CV {'found' if has_cv else 'missing'}; photo {'found' if has_photo else 'missing'}")


if __name__ == "__main__":
    main()
