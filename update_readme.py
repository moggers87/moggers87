from datetime import timezone
import json
import urllib.request

from dateutil.parser import parse
import feedparser


PYTHON_PROJECTS = [
    "django-two-factor-auth",
    "multiblock",
    "lmtpd",
    "django-sendfile2",
    "exhibition",
    "salmon-mail",
    "city",
    "inboxen",
    "sorry",
    "regent",
    "django-csrf-session",
    "PyPump",
    "lazycat",
]

NPM_PROJECTS = [
    "smallquery",
]

PYPI_URL = "https://pypi.org/pypi/{project}/json"
NPM_URL = "https://skimdb.npmjs.com/registry/{project}"

BLOG_URLS = {
    "blog": "https://moggers87.co.uk/blog/atom.xml",
    "art": "https://moggers87.co.uk/art/atom.xml",
    "food": "https://moggers87.co.uk/food/atom.xml",
}

README_TMPL = """
# moggers87

## Latest releases

{latest_releases}

## From moggers87.co.uk

{the_blog}

## Elsewhere

[Twitter](https://twitter.com/moggers87)
[Mastodon](https://mastodon.xyz/moggers87)
[Moggers87.co.uk](https://moggers87.co.uk)
[Very Little Gravitas Indeed Ltd](vlgi.space)
"""

PROJECT_TMPL = "- **{name}** {version} released on *{date}*"
BLOG_TMPL = "- ({type}) **{title}** *{date}*"


def _fixup_tz(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def generate_readme():
    readme_text = README_TMPL.format(
        latest_releases="\n".join(generate_latest_releases()),
        the_blog="\n".join(generate_the_blog())
    )
    with open("README.md", "w") as readme_file:
        readme_file.write(readme_text)


def generate_latest_releases():
    releases = []
    releases.extend(get_npm_releases())
    releases.extend(get_pypi_releases())
    releases = sorted(releases, key=lambda x: x["date"], reverse=True)

    for proj in releases[:5]:
        yield PROJECT_TMPL.format(**proj)


def get_npm_releases():
    for project in NPM_PROJECTS:
        with urllib.request.urlopen(NPM_URL.format(project=project)) as url:
            data = json.loads(url.read().decode())
            version = data["dist-tags"]["latest"]
            date = _fixup_tz(parse(data["time"][version]))
            yield {
                "name": data["name"],
                "version": version,
                "date": date,
            }


def get_pypi_releases():
    for project in PYTHON_PROJECTS:
        with urllib.request.urlopen(PYPI_URL.format(project=project)) as url:
            data = json.loads(url.read().decode())
            version = data["info"]["version"]
            date = _fixup_tz(parse(data["releases"][version][0]["upload_time"]))
            yield {
                "name": data["info"]["name"],
                "version": version,
                "date": date,
            }


def generate_the_blog():
    posts = []
    for typ, url in BLOG_URLS.items():
        for post in feedparser.parse(url)["entries"]:
            date = _fixup_tz(parse(post["published"]))
            posts.append({
                "type": typ,
                "title": post["title"],
                "date": date,
            })

    posts = sorted(posts, key=lambda x: x["date"], reverse=True)

    for pst in posts[:5]:
        yield BLOG_TMPL.format(**pst)


if __name__ == "__main__":
    generate_readme()
