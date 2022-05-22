import os
import asyncio
import urllib.error
from urllib.request import urlopen
from client import Client
from readme import Readme
from utils import parse_header


class Main:
    TARGET = 'https://api.github.com/graphql'

    def __init__(self, tags=tuple()):
        self.CLIENT = Client(os.getenv('ACCESS_TOKEN'))
        self.TAGS = tags

    async def run(self):
        repos = await self.get_all_repos()
        filtered = self.filter_repos(repos)
        readme = Readme(filtered)
        readme.generate()

    async def get_all_repos(self):
        """Returns all public repositories the user contributed to."""

        repos = []
        has_next_owned = True
        has_next_contrib = True
        owned_cursor = 'null'
        contrib_cursor = 'null'
        while has_next_owned or has_next_contrib:
            r = await self.get_repos_page(owned_cursor, contrib_cursor)

            owned = r.get('data', {}).get('viewer', {}).get('repositories', {})
            repos += owned.get('nodes', [])
            page_info = owned.get('pageInfo', {})
            has_next_owned = page_info.get('hasNextPage', False)
            if has_next_owned:
                owned_cursor = page_info.get('endCursor', 'null')
            else:
                owned_cursor = 'null'

            contributed = r.get('data', {}).get('viewer', {}).get('repositoriesContributedTo', {})
            repos += contributed.get('nodes', [])
            page_info = contributed.get('pageInfo', {})
            has_next_contrib = page_info.get('hasNextPage', False)
            if has_next_contrib:
                contrib_cursor = page_info.get('endCursor', 'null')
            else:
                contrib_cursor = 'null'
        return repos

    def filter_repos(self, repos):
        """Filters repositories and keeps those with tags in SELF.TAGS"""

        print('\n[~] Parsing repositories:')
        filtered = {}
        for r in repos:
            name = r.get('name', '')
            owner = r.get('owner', {}).get('login', '')
            default_branch = r.get('defaultBranchRef', {}).get('name', '')
            url = f'https://raw.githubusercontent.com/{owner}/{name}/{default_branch}/README.md'
            try:
                contents = [x.decode('utf-8').strip() for x in urlopen(url)]
                header = parse_header(contents)
                if header is not None and any(x in header['tags'] for x in self.TAGS):
                    r['header'] = header
                    category = header['category']
                    if category not in filtered:
                        filtered[category] = []
                    filtered[category].append(r)
            except urllib.error.HTTPError:
                print(f" !  Invalid URL: '{url}'")
        return filtered

    async def get_repos_page(self, owned_cursor, contrib_cursor):
        """Returns one page of repositories."""

        with open('resources/repositories.query', 'r') as file:
            query = file.read()
        query = query.replace('__OWNED_CURSOR__', owned_cursor)
        query = query.replace('__CONTRIBUTED_CURSOR__', contrib_cursor)
        return await self.CLIENT.request(self.TARGET, query)


if __name__ == '__main__':
    main = Main(tags=('mlpi',))
    asyncio.run(main.run())
