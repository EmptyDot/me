from __future__ import annotations
from requests import Request, Session, Response
from urllib.parse import urlencode
import dateutil.parser
from collections import OrderedDict
import os

API_TOKEN = os.environ["API_TOKEN"]


def get_user_repos() -> Response:
    path = "https://api.github.com/user/repos"
    query_params = {"visibility": "public", "sort": "created", "direction": "desc"}
    url = f"{path}?{urlencode(query_params, encoding='utf-8')}"
    s = Session()
    req = Request(
        "GET",
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {API_TOKEN}",
        },
    )

    prepped = s.prepare_request(req)
    response = s.send(prepped)
    response.raise_for_status()
    return response


def get_repo_info():
    repos_info = OrderedDict()

    repos = get_user_repos().json()
    sorted_repos = sorted(
        repos, key=lambda i: (i["created_at"], i["full_name"]), reverse=True
    )
    for repo in sorted_repos:
        # get the year it was created
        created = repo["created_at"]
        date = dateutil.parser.isoparse(created)
        year = date.year
        # get the repo name
        full_name: str = repo["full_name"]
        name = full_name.replace("EmptyDot/", "")
        # get the description
        description = repo["description"]
        # get url
        url = repo["html_url"]

        repo_dict = {"year": year, "name": name, "description": description, "url": url}
        try:
            repos_info[year].append(repo_dict)
        except KeyError:
            repos_info[year] = [repo_dict]
    return repos_info


def build_string():
    strings = []
    for year, repos in get_repo_info().items():
        strings.append(f"## {year}")
        for repo in repos:
            s = f"### [{repo['name']}]({repo['url']})\n" f"{repo['description']}\n"
            strings.append(s)

    return "\n".join(strings)


def write_repos_file():
    with open("repos.md", "w") as file:
        file.write("# Projects\n\n")
        file.write(build_string())


def create_page(filenames):
    with open("README.md", "w") as outfile:
        for filename in filenames:
            with open(filename, "r") as infile:
                for line in infile:
                    outfile.write(line)


if __name__ == "__main__":
    write_repos_file()
    create_page(["about_me.md", "repos.md"])
