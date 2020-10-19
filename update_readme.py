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
    #"city",
    "inboxen",
    #"sorry",
    #"regent",
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

Hey it's me.

I write code for living. [Send me money](https://ko-fi.com/moggers87) or
consider [hiring me](vlgi.space) if you like my work.

## Latest releases

{latest_releases}

## [From moggers87.co.uk](https://moggers87.co.uk)

{the_blog}

## Elsewhere

- [Twitter](https://twitter.com/moggers87)
- [Mastodon.xyz](https://mastodon.xyz/moggers87)

"""

PROJECT_TMPL = """- <a href="{url}">{name}</a> {version} released on {date:%Y-%m-%d}"""
BLOG_TMPL = """- ({type}) <a href="{url}">{title}</a> posted on {date:%Y-%m-%d}"""


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
                # there doesn't seem to be a copy of this URL in the API. Am I
                # doing something wrong?
                "url": "https://www.npmjs.com/package/{}".format(data["name"]),
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
                "url": data["info"]["package_url"],
            }


def generate_the_blog():
    posts = []
    for typ, url in BLOG_URLS.items():
        feed = feedparser.parse(url)
        for post in feed["entries"]:
            date = _fixup_tz(parse(post["published"]))
            posts.append({
                "type": typ,
                "title": post["title"],
                "date": date,
                "url": post["link"],
            })

    posts = sorted(posts, key=lambda x: x["date"], reverse=True)

    for pst in posts[:5]:
        yield BLOG_TMPL.format(**pst)


if __name__ == "__main__":
    generate_readme()
